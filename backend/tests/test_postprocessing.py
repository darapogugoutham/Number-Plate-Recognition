from app.cv.postprocessing import clean_plate_text, correct_common_ocr_errors, validate_plate


def test_clean_plate_text_removes_noise():
    assert clean_plate_text(" TX ABC-1234\n") == "TXABC1234"


def test_validate_plate_accepts_reasonable_plate():
    assert validate_plate("TXABC1234")


def test_validate_plate_rejects_short_plate():
    assert not validate_plate("A1")


def test_correct_common_errors_only_biases_last_digits():
    assert correct_common_ocr_errors("ABC12O") == "ABC120"
