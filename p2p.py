import random
import database as sql_

from main import p2p

async def create_bill(amount: int, lifetime: int, userid):
    comment = f'{userid}_{random.randint(1000, 9999)}'
    bill = p2p.bill(amount=amount, lifetime=lifetime, comment=comment)
    await sql_.add_bill(userid, bill.bill_id, amount)

    return bill.pay_url
