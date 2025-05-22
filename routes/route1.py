from flask import Blueprint, request, jsonify
from models.db import mongo
from alipay import AliPay
import qrcode
import io
import base64
import time

bp = Blueprint("route1", __name__)

@bp.route("/set_parklot", methods=["POST"])
def set_parklot():
    data = request.json or {}
    mac = data.get("mac")
    val = data.get("val")
    if mac is None or val not in [0, 1]:
        return jsonify({"error": "Invalid parameters"}), 400

    # 查询原状态
    old = mongo.db.parklots.find_one({"mac": mac})
    old_val = old["val"] if old else None

    result = mongo.db.parklots.update_one(
        {"mac": mac},
        {"$set": {"val": val}},
        upsert=True
    )

    # 如果由空变为占用，重置该mac所有订单为未付费
    if old_val == 0 and val == 1:
        mongo.db.orders.update_many(
            {"mac": mac},
            {"$set": {"status": "unpaid"}},
            upsert=True
        )

    if result.matched_count > 0 or result.upserted_id:
        return jsonify({"message": "Parklot status updated"}), 201
    else:
        return jsonify({"error": "Parklot not found"}), 404

@bp.route("/free_count", methods=["GET"])
def free_count():
    count = mongo.db.parklots.count_documents({"val": 0})
    return str(count) + "\n"

# ...existing code...

@bp.route("/get_parklots", methods=["GET"])
def get_parklots():
    parklots = list(mongo.db.parklots.find({}, {"_id": 0, "mac": 1, "val": 1}))
    return jsonify(parklots)
# ...existing code...


# 沙箱参数（请替换为你自己的）
ALIPAY_APPID = "2021000149601594"
ALIPAY_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEowIBAAKCAQEAhpTFwten1ysasNj9qax/pbOrQnuBcgdJx3mSp8nbMCFeNamwKKffjj0N2C6VvJ1YJN2U+LrS4fAe49lIm+nTutOXcop/xWxsW4yONzV6VwRQRDR7fLsof0PgDCEoSYaGNrlqeaBvzhwE0qdiWspok84ICFczE5WLh8yqrSWcHq3Uj2V93ZXUDZnawQB3UAOP1sLPnf8Ufx8nDifsSFIIedSNMpg9FpJ4H3sFH0bfIQC7eQbN7sUGCPaAThsM51S5nQPHGKHL5Q6U6MovlQ1hLhKZ34fcBQDi4AasLcYseaHIQLc0bTrgu89KO4dXLtgq5gw7I0JsbK6r+nHr+rFBCwIDAQABAoIBABGkz4iL3WVIMWeeCyODififZYSBzKa2beXI+oEk5aeZuFAwvveViqmLN5VwBhGET1oF8tHpLFySrnoQsoQ+U5PaybAqmDW50TrvYnW6fR+LYTqP5uCjaNvGekkcz7tT96SVCnCHqCDNa5RyfWKJxswZ5tOxGvEmWfSj0HyCwcUDtHmIVwDHW/yFiE5apkcLS/kw4Lg3UpUYeRnEB2NHm9O1PUmWl/VhOPDTjXEQyA6esgH8CCNnQe10dRZ+cEA3cDZHYnHIbxDZgvYGmocGMaBvvfrNZgYnpWVux44WYyZ4ome1ZedUSESuyLStINTose9ufw1EFmJymuimvnyH0YECgYEAvy2I4vjmE+Q+ucl5oo9aQyv0Qloq4InlTUEtlKwWAzlTkV+yPrYYGBrQqnuqXX8zNElpeAxWQxh2txOqasAK1Yd2UUKOzPYwNuqW4msUEYkmNv+XPGqMf8WGpaQWtH0K9MkNre3/YMPClp74hYrE8QCZjOPsL/y4J6x2jIwOElUCgYEAtDaTLH+rjnd+QyzU4CS55RWvvwzEJj1bwHe651zcOdS7l0UyOSI7BWFBDMu1gDg++CYjeDmw3fjj0m+6Uw6/JuSzVpN8U4NZuYmYWaEiDS6nyQ5R2ahZWLPhXd8UfzsqWHZ57Jz2Yxk1xw3YEfARHYcLRuzFNCNrZIFrMJ2lJd8CgYAettEULgrAzV2qeYz6Ke/FdO1UL6pN0rmtNLh+9zq+H9qmM2qumpC6Zqx5h06yoLn4P4cbS1gchXSlKxqo9duHvLCsk3XfxfmvCPdevvdFbfRex6djhHa4HGLqf7dKHgDBnP9+nwr1X94GVtn0knvbgE4rDX8nooFvlkyhferQ1QKBgC0h4dfqHW/vkyqFpsZ/zCKIPNxu+QzOnxTjp2ZcBjdhhJ2M0dgnL3rYcW8f8VOsQnDpNEbew+HDfGLuYk58yfiWnCdZhnBv29+wivwfc6Szg4fB01PcaovheNaGkN6QVbmT6lMMuFP3M1WnrO5JHjAz6uoXUAgPusyP8OVbBconAoGBAImOzWFTPfBSJyIBtv0O3M2KjwE/QaiBmJ7uIibL1pOLvVYI134QTY3trmktM4CcQcshSXK2MvQit2sLpzWwkkfxkk4mgugKjc2jq/bJs70OSxQiioCqDkubW0oZ4OYtz3q9Hv6U3eicnWQYhmOdrZdETqXIu4LuBR6AklpPNYOm
-----END PRIVATE KEY-----"""
ALIPAY_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoPNhRCAIfTNAVkfrdY2Tl64ywS+QVDY5KB10DnK6nErEmmHN6USGNuEZb+p8wB2HXcSOJqY5NfSmaXfVpEg836kCgMMAWWk3RGjirKw+RYMrNqZR9qsd0d9nxqKKwts0b2Yud5mcGUQlb1AuCyEZiSXToQ3ZB72M1/tLcLC4cTqcnbv2eF6Zrt8H/jXR1ECTxurODzSw9bJ/SPE1xnktAcwj2fl+x8HezXqclA/N7+df5PqBa82yGkstOonjuxb+6BmWOk27251w+FaPuCFS4LVe3QtlFD0CqnzzGgnTizFfSbKusy6ntVmqU5yj4n9m+47eFnnlWVkLmMU8MM60IwIDAQAB
-----END PUBLIC KEY-----"""
ALIPAY_GATEWAY = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"


def get_alipay_client():
    return AliPay(
        appid=ALIPAY_APPID,
        app_notify_url="http://43.136.31.127:5000/alipay_notify",  # 异步回调
        app_private_key_string=ALIPAY_PRIVATE_KEY,
        alipay_public_key_string=ALIPAY_PUBLIC_KEY,
        sign_type="RSA2",
        debug=True
    )

@bp.route("/pay_qr", methods=["POST"])
def pay_qr():
    data = request.json
    mac = data.get("mac")
    fee = data.get("fee")
    order_id = f"{mac}_{int(time.time())}"
    alipay = get_alipay_client()
    order_string = alipay.api_alipay_trade_precreate(
        subject=f"停车费-{mac}",
        out_trade_no=order_id,
        total_amount=str(fee)
    )
    qr_url = order_string["qr_code"]
    # 生成二维码图片并转为base64
    img = qrcode.make(qr_url)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_b64 = base64.b64encode(buf.getvalue()).decode()
    # 记录订单到数据库
    mongo.db.orders.insert_one({"mac": mac, "order_id": order_id, "fee": fee, "status": "unpaid"})
    return jsonify({"qr_img": img_b64, "order_id": order_id})
  

@bp.route("/can_open_gate", methods=["POST"])
def can_open_gate():
    data = request.json or {}
    mac = data.get("mac")
    if not mac:
        return "2"
    lot = mongo.db.parklots.find_one({"mac": mac})
    if not lot:
        return "2"
    if lot.get("val") == 0:
        return "1"
    order = mongo.db.orders.find_one({"mac": mac, "status": "paid"})
    if order:
        return "1"
    return "0"

@bp.route("/alipay_notify", methods=["POST"])
def alipay_notify():
    # 支付宝会以 form-data 方式推送数据
    data = request.form.to_dict()
    # 获取签名并移除
    signature = data.pop("sign", None)
    alipay = get_alipay_client()
    # 校验签名
    success = alipay.verify(data, signature)
    if not success:
        return "fail"

    # 判断支付状态
    if data.get("trade_status") in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
        order_id = data.get("out_trade_no")
        # 更新订单状态
        mongo.db.orders.update_one(
            {"order_id": order_id},
            {"$set": {"status": "paid"}}
        )
        return "success"
    return "fail"