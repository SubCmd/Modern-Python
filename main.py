from collections import Counter
from tkinter import NO

type FunnelEvent = dict[str, str | int]
type FunnelRow = dict[str, str | int | float | bool]

def analyze_funnel(
    events: list[FunnelEvent],
    target_event: str | None = None,
) -> list[FunnelRow] | None:
    f"""퍼널 이벤트 목록을 받아 단계별 전환율을 계산한다.

    Args:
        events: 각 이벤트는 {"step": "장바구니", "user_id": 123} 형태.
        target_event: 하이라이트할 특정 단계. None이면 전체 표시.

    Returns:
        단계별 카운트 + 전환율 리스크. 이벤트가 비어있으면 None.
    """
    if not events:
        return None

    total = len(events)
    step_counts = Counter(event.get("step", "unknown") for event in events)

    return [
        {
            "step": step,
            "count": count,
            "rate": f"{count / total:.1%}",          # f-string + :.1%
            **({"is_target": True}                    # 조건부 dict 병합
               if target_event is not None and step == target_event
               else {}),
        }
        for step, count in step_counts.items()
    ]
