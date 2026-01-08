def formatted_time():
    from datetime import datetime
    now = datetime.now()
    formatted_datetime = now.strftime("%d-%m-%Y_%Hh%Mm%Ss")
    
    return formatted_datetime
