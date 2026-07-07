import jdatetime 
from datetime import datetime

def to_jalali(date: datetime) -> str:
    return jdatetime.datetime.fromgregorian(
        datetime=date
    ).strftime("%Y/%m/%d %H:%M")