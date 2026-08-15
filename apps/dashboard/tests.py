import re
from pathlib import Path
from tempfile import TemporaryDirectory

from datetime import timedelta

from django.test import RequestFactory
from django.test import TestCase
from django.test import override_settings
from django.template.loader import render_to_string
from django.utils import timezone

from apps.encryption.services import HybridEncryptionService
from apps.medical_records.models import MedicalRecord
from apps.users.models import User

from .services.chart_service import ChartService
from .services.dashboard_service import DashboardService


class PredictionTrendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="trend-user",
            password="test-password",
        )

    def create_record(self, prediction_time):
        return MedicalRecord.objects.create(
            created_by=self.user,
            encrypted_payload="payload",
            encrypted_aes_key="key",
            ephemeral_public_key="public-key",
            integrity_hash="0" * 64,
            prediction_time=prediction_time,
        )

    def test_prediction_trend_includes_zero_count_days(self):
        first_day = timezone.now().replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0,
        )
        self.create_record(first_day)
        self.create_record(first_day + timedelta(days=2))

        trend = ChartService.prediction_trend()

        self.assertEqual(trend["values"], [1, 0, 1])


class DecryptedRecordTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="record-user",
            password="test-password",
        )
        self.request = RequestFactory().get("/records/example/")
        self.private_directory = TemporaryDirectory()
        key_pair = HybridEncryptionService.generate_key_pair()
        self.private_key_path = (
            Path(self.private_directory.name) / "private_key.pem"
        )
        self.private_key_path.write_bytes(key_pair.private_key_pem)
        public_key = HybridEncryptionService.load_public_key(
            self._write_public_key(key_pair.public_key_pem)
        )
        self.payload = {
            "patient_id": "patient-001",
            "clinical_inputs": {
                "heart_rate": 82,
                "systolic_bp": 124,
            },
        }
        encrypted = HybridEncryptionService.encrypt_json(
            self.payload,
            public_key,
        )
        self.record = MedicalRecord.objects.create(
            created_by=self.user,
            encrypted_payload=encrypted.ciphertext_b64,
            encrypted_aes_key=encrypted.encrypted_aes_key_b64,
            ephemeral_public_key=encrypted.ephemeral_public_key_b64,
            integrity_hash=encrypted.integrity_hash,
        )

    def tearDown(self):
        self.private_directory.cleanup()

    def _write_public_key(self, public_key):
        path = Path(self.private_directory.name) / "public_key.pem"
        path.write_bytes(public_key)
        return path

    def test_dashboard_service_returns_decrypted_payload(self):
        with override_settings(
            FOG_ECC_PRIVATE_KEY_PATH=self.private_key_path
        ):
            result = DashboardService.get_decrypted_record(
                record_id=self.record.pk,
                user=self.user,
                request=self.request,
            )

        self.assertEqual(result["record_id"], self.record.pk)
        self.assertEqual(result["data"], self.payload)
        self.assertEqual(
            result["clinical_input_rows"],
            [
                {"label": "Heart Rate", "value": 82},
                {"label": "Systolic BP", "value": 124},
            ],
        )

    def test_record_detail_renders_clinical_inputs_as_rows(self):
        payload = {
            "clinical_inputs": {
                "age": 53.0,
                "heart_rate": 155.0,
                "systolic_bp": 0,
            },
        }

        rendered = render_to_string(
            "dashboard/record_detail.html",
            {
                "integrity_ok": True,
                "record": {
                    "record_id": self.record.pk,
                    "data": payload,
                    "clinical_input_rows": [
                        {"label": "Age", "value": 53.0},
                        {"label": "Heart Rate", "value": 155.0},
                        {"label": "Systolic BP", "value": 0},
                    ],
                },
            },
        )

        self.assertNotIn(str(payload["clinical_inputs"]), rendered)
        self.assertIn("Age", rendered)
        self.assertIn("Heart Rate", rendered)
        self.assertIn("Systolic BP", rendered)
        self.assertRegex(rendered, re.compile(r">\s*0\s*</td>"))
