from quart import Quart, jsonify, request
from temporalio.client import Client

from activities import Purchase
from workflows import OneClickBuyWorkflow, PurchaseStatus

app = Quart(__name__)


@app.before_serving
async def startup():
    global client
    client = await Client.connect("localhost:7233")


@app.route("/purchase", methods=["POST"])
async def handle_purchase():
    data = await request.json
    print(f"Received purchase request: {data}")

    handle = await client.start_workflow(
        OneClickBuyWorkflow.run,
        Purchase(
            item_id=data.get("item_id", "unknown"),
            user_id=data.get("user_id", "unknown"),
        ),
        id=f"{data.get('user_id', 'unknown')}-purchase1",
        task_queue="my-task-queue",
    )

    await handle.cancel()

    status = await handle.query(OneClickBuyWorkflow.current_status)
    assert status == PurchaseStatus.CANCELLED

    return jsonify({"status": "success", "workflow_status": status.name}), 200


if __name__ == "__main__":
    app.run(port=5001, debug=True)
