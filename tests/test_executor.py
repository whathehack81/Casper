from casper.tools.executor import export_result, run_command


def test_run_command_success():
    result = run_command(["python", "-c", "print('hello')"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "hello"
    assert result.stderr == ""
    assert result.sha256

    exported = export_result(result)
    assert exported["command"] == ["python", "-c", "print('hello')"]
