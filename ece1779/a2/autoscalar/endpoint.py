from flask import request, render_template, url_for
from flask import json
from autoscalar import autoscalar_app, cloudwatch, autoscalar

# send the new memcache pool size to manager
@autoscalar_app.route('/api/UpdatePoolSize', methods=['GET'])
def update_pool_size():
    instruction = autoscalar.get_new_scalar()
    response = autoscalar_app.response_class(
        response=json.dumps({"success": "true", "instruction":instruction}),
        status=200,
        mimetype='application/json')
    return response

# reset threshold paramneter
@autoscalar_app.route('/api/UpdateThreshold', methods=['POST'])
def update_threshold():
    autoscalar.reset_threshold()
    response = autoscalar_app.response_class(
        response=json.dumps({"success": "true"}),
        status=200,
        mimetype='application/json'
    )
    return response