import sys
import pytest
from opengd77_chirp_csv_coverter import main, DEFAULT_OPERATION, VALID_OPERATIONS

def make_fake_transform_channels(monkeypatch):
    called = {}
    def fake_transform_channels(operation, input_file, output_file, start_channel):
        called['operation'] = operation
        called['input_file'] = input_file
        called['output_file'] = output_file
        called['start_channel'] = start_channel
    monkeypatch.setattr("opengd77_chirp_csv_coverter.transform_channels", fake_transform_channels)
    return called

def test_main_defaults(monkeypatch):
    called = make_fake_transform_channels(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["prog"])
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    main()
    assert called['operation'] == DEFAULT_OPERATION
    assert called['input_file'] == VALID_OPERATIONS[DEFAULT_OPERATION]["default_input_file"]
    assert called['output_file'] == VALID_OPERATIONS[DEFAULT_OPERATION]["default_output_file"]
    assert called['start_channel'] == 0

def test_main_only_operation(monkeypatch):
    called = make_fake_transform_channels(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["prog", "chirp"])
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    main()
    assert called['operation'] == "chirp"
    assert called['input_file'] == VALID_OPERATIONS["chirp"]["default_input_file"]
    assert called['output_file'] == VALID_OPERATIONS["chirp"]["default_output_file"]
    assert called['start_channel'] == 0

def test_main_only_input_file(monkeypatch):
    called = make_fake_transform_channels(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["prog", "gd77", "custom_input.csv"])
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    main()
    assert called['input_file'] == "custom_input.csv"
    assert called['output_file'] == VALID_OPERATIONS["gd77"]["default_output_file"]
    assert called['start_channel'] == 0

def test_main_only_input_and_output_file(monkeypatch):
    called = make_fake_transform_channels(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["prog", "chirp", "in.csv", "out.csv"])
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    main()
    assert called['input_file'] == "in.csv"
    assert called['output_file'] == "out.csv"
    assert called['start_channel'] == 0

def test_main_negative_start_channel(monkeypatch):
    called = make_fake_transform_channels(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["prog", "gd77", "a.csv", "b.csv", "-3"])
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    main()
    assert called['start_channel'] == -3

def test_main_zero_start_channel(monkeypatch):
    called = make_fake_transform_channels(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["prog", "chirp", "a.csv", "b.csv", "0"])
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    main()
    assert called['start_channel'] == 0

def test_main_start_channel_non_integer(monkeypatch):
    called = make_fake_transform_channels(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["prog", "gd77", "input.csv", "output.csv", "notanint"])
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    with pytest.raises(ValueError):
        main()

def test_main_gd77_with_args(monkeypatch):
    called = make_fake_transform_channels(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["prog", "gd77", "in.csv", "out.csv", "5"])
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    main()
    assert called['operation'] == "gd77"
    assert called['input_file'] == "in.csv"
    assert called['output_file'] == "out.csv"
    assert called['start_channel'] == 5

def test_main_chirp_with_partial_args(monkeypatch):
    called = make_fake_transform_channels(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["prog", "chirp", "custom_in.csv"])
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    main()
    assert called['operation'] == "chirp"
    assert called['input_file'] == "custom_in.csv"
    assert called['output_file'] == VALID_OPERATIONS["chirp"]["default_output_file"]
    assert called['start_channel'] == 0

def test_main_invalid_operation(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "invalidop"])
    printed = {}
    def fake_print(msg):
        printed['msg'] = msg
    monkeypatch.setattr("builtins.print", fake_print)
    with pytest.raises(SystemExit):
        main()
    assert "Invalid operation" in printed['msg']

def test_main_too_many_args(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "gd77", "a", "b", "c", "d"])
    printed = {}
    def fake_print(msg):
        printed['msg'] = msg
    monkeypatch.setattr("builtins.print", fake_print)
    with pytest.raises(SystemExit):
        main()
    assert "Too many arguments" in printed['msg']