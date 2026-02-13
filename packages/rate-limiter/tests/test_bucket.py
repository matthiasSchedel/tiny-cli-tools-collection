from rate_limiter.bucket import BucketState, TokenBucket


def test_bucket_consumption_and_refill() -> None:
    bucket = TokenBucket(BucketState(tokens=1.0, last_refill=0.0, capacity=2, refill_rate=1.0))
    assert bucket.try_consume(now=0.0)
    assert not bucket.try_consume(now=0.0)
    assert bucket.try_consume(now=1.1)
