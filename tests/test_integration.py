import pytest
from unittest.mock import patch, MagicMock
from ai_pipeline.cli import app
from ai_pipeline.detector import Stack
from typer.testing import CliRunner

runner = CliRunner()

@patch('ai_pipeline.generator.requests.post')
@patch('ai_pipeline.cli.get_best_provider')
@patch('ai_pipeline.cli.scan_repo')
@patch('ai_pipeline.cli.detect_stack')
def test_full_generate_flow(mock_detect, mock_scan, mock_provider, mock_post):
    # Configura os Mocks
    mock_scan.return_value = ["package.json", "Dockerfile"]
    mock_detect.return_value = Stack(
        language="Node.js",
        language_version="18",
        tests="Jest",
        container=True
    )
    mock_provider.return_value = ("FAKE_KEY", "sk-fake-key")

    # Simula resp da IA
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": "```yaml\nname: CI\non: push\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v3\n```"
            }
        }]
    }
    mock_post.return_value = mock_response

    # Command
    result = runner.invoke(app, ["generate"])

    assert result.exit_code == 0
    assert "Success!" in result.stdout
    assert "Pipeline generated at .github/workflows/ci.yml" in result.stdout
