import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.scheduler.jobs import create_scheduler, run_batch


def test_run_batch_pre_market():
    with patch("app.scheduler.jobs.build_graph") as mock_build:
        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(return_value={"batch_type": "pre_market"})
        mock_build.return_value = mock_graph

        result = run_batch("pre_market")

        mock_build.assert_called_once()
        mock_graph.ainvoke.assert_called_once()
        assert result["batch_type"] == "pre_market"


def test_run_batch_post_market():
    with patch("app.scheduler.jobs.build_graph") as mock_build:
        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(return_value={"batch_type": "post_market"})
        mock_build.return_value = mock_graph

        result = run_batch("post_market")
        assert result["batch_type"] == "post_market"


def test_run_batch_handles_error():
    with patch("app.scheduler.jobs.build_graph") as mock_build:
        mock_build.side_effect = RuntimeError("API down")
        result = run_batch("pre_market")
        assert result["status"] == "failed"
        assert "API down" in result["error"]


def test_create_scheduler():
    scheduler = create_scheduler()
    jobs = scheduler.get_jobs()
    assert len(jobs) == 2
    job_names = [j.name for j in jobs]
    assert "pre_market_batch" in job_names
    assert "post_market_batch" in job_names
