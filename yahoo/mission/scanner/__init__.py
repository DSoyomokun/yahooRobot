"""
Scanner module for test paper processing.
"""

# Import main function (lazy import to avoid circular dependencies)
def process_test_image(*args, **kwargs):
    """Main entry point for processing test images."""
    from .pipeline import process_test_image as _process_test_image
    return _process_test_image(*args, **kwargs)

__all__ = ['process_test_image']
