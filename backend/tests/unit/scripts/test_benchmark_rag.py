"""Unit tests for benchmark_rag script."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.benchmark_rag import (
    BenchmarkResult,
    calculate_percentile,
    load_queries,
    run_benchmark_query,
)


def test_benchmark_result_to_dict():
    """Test BenchmarkResult conversion to dictionary."""
    result = BenchmarkResult("test query")
    result.latency_ms = 125.5
    result.num_results = 3
    result.result_paths = ["path1", "path2", "path3"]
    
    result_dict = result.to_dict()
    
    assert result_dict["query"] == "test query"
    assert result_dict["latency_ms"] == 125.5
    assert result_dict["num_results"] == 3
    assert result_dict["result_paths"] == ["path1", "path2", "path3"]


def test_benchmark_result_with_ground_truth():
    """Test BenchmarkResult with ground truth for accuracy calculation."""
    result = BenchmarkResult("test query", ground_truth=["path1", "path2"])
    result.result_paths = ["path1", "path3", "path4"]
    
    accuracy = result.calculate_accuracy()
    
    # 1 out of 2 ground truth items found
    assert accuracy == 0.5
    
    result_dict = result.to_dict()
    assert "accuracy" in result_dict
    assert result_dict["accuracy"] == 0.5


def test_benchmark_result_with_error():
    """Test BenchmarkResult with error."""
    result = BenchmarkResult("test query")
    result.error = "Something went wrong"
    
    result_dict = result.to_dict()
    
    assert "error" in result_dict
    assert result_dict["error"] == "Something went wrong"


def test_load_queries_from_array():
    """Test loading queries from JSON array."""
    queries = ["query 1", "query 2", "query 3"]
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(queries, f)
        temp_file = Path(f.name)
    
    try:
        loaded_queries = load_queries(temp_file)
        
        assert loaded_queries == queries
    finally:
        temp_file.unlink()


def test_load_queries_from_object():
    """Test loading queries from JSON object with 'queries' key."""
    data = {
        "queries": [
            {"query": "test 1", "expected_paths": ["path1"]},
            {"query": "test 2", "expected_paths": ["path2"]},
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(data, f)
        temp_file = Path(f.name)
    
    try:
        loaded_queries = load_queries(temp_file)
        
        assert len(loaded_queries) == 2
        assert loaded_queries[0]["query"] == "test 1"
    finally:
        temp_file.unlink()


def test_load_queries_invalid_format():
    """Test loading queries with invalid format."""
    data = {"invalid": "format"}
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(data, f)
        temp_file = Path(f.name)
    
    try:
        with pytest.raises(ValueError):
            load_queries(temp_file)
    finally:
        temp_file.unlink()


def test_load_queries_file_not_found():
    """Test loading queries from nonexistent file."""
    with pytest.raises(FileNotFoundError):
        load_queries(Path("/nonexistent/file.json"))


@patch("scripts.benchmark_rag.RAGPipeline")
def test_run_benchmark_query_success(mock_pipeline_class):
    """Test running a successful benchmark query."""
    mock_pipeline = MagicMock()
    mock_pipeline.search.return_value = [
        {"metadata": {"content_path": "path1"}},
        {"metadata": {"content_path": "path2"}},
        {"metadata": {"content_path": "path3"}},
    ]
    
    result = run_benchmark_query(mock_pipeline, "test query", top_k=5)
    
    assert result.query == "test query"
    assert result.latency_ms is not None
    assert result.latency_ms > 0
    assert result.num_results == 3
    assert result.result_paths == ["path1", "path2", "path3"]
    assert result.error is None


@patch("scripts.benchmark_rag.RAGPipeline")
def test_run_benchmark_query_error(mock_pipeline_class):
    """Test running a benchmark query that raises an error."""
    mock_pipeline = MagicMock()
    mock_pipeline.search.side_effect = Exception("Search failed")
    
    result = run_benchmark_query(mock_pipeline, "test query", top_k=5)
    
    assert result.error == "Search failed"


def test_calculate_percentile():
    """Test percentile calculation."""
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    p50 = calculate_percentile(values, 50)
    assert p50 == 5.5  # Median of even-length list
    
    p95 = calculate_percentile(values, 95)
    assert p95 >= 9  # Should be near top
    
    p0 = calculate_percentile(values, 0)
    assert p0 == 1  # Minimum
    
    p100 = calculate_percentile(values, 100)
    assert p100 == 10  # Maximum


def test_calculate_percentile_empty_list():
    """Test percentile calculation with empty list."""
    result = calculate_percentile([], 50)
    assert result == 0.0


def test_calculate_percentile_single_value():
    """Test percentile calculation with single value."""
    result = calculate_percentile([42], 50)
    assert result == 42
