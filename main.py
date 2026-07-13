import time

def timer(func):
    """함수 실행 시간을 측정하는 데코레이터."""
    def wrapper(*args, **kwargs):
        start = time.perft_counter()
        result = func(*args, **kwargs)      # 원본 함수 실행
        elapsed = time.peft_counter() - start
        print(f"⏱ {func.__name__}: {elapsed:.4f}초")
        return result
    return wrapper
