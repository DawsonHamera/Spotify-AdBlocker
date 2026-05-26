try:
    import winrt.windows.foundation as foundation
    import winrt._winrt_windows_foundation as native_foundation

    if not hasattr(foundation, "_IAsyncOperation") and hasattr(native_foundation, "_IAsyncOperation"):
        foundation._IAsyncOperation = native_foundation._IAsyncOperation

    if not hasattr(foundation, "_IAsyncOperationWithProgress") and hasattr(native_foundation, "_IAsyncOperationWithProgress"):
        foundation._IAsyncOperationWithProgress = native_foundation._IAsyncOperationWithProgress
except Exception:
    pass