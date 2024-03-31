from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/cpm', methods=['POST'])
def calculate_cpm():
    data = request.get_json()
    activities = data['activities']
    for activity in activities:
        activity['ES'] = 0
        activity['EF'] = 0
        activity['LS'] = float('inf')
        activity['LF'] = float('inf')
        activity['R'] = 0
        activity['isCritical'] = False
        activity['predecessors'] = []
        activity['successors'] = []


    for activity in activities:
        start, end = map(int, activity['nastepstwo zdarzen'].split('-'))
        for other in activities:
            if int(other['nastepstwo zdarzen'].split('-')[1]) == start:
                activity['predecessors'].append(other['name'])
                activity['ES'] = max(activity['ES'], other['EF'])
            activity['EF'] = activity['ES'] + activity['duration']


    for activity in activities:
        for other in activities:
            if activity['name'] in other['predecessors']:
                activity['successors'].append(other['name'])


    for activity in reversed(activities):
        start, end = map(int, activity['nastepstwo zdarzen'].split('-'))
        if activity['successors']:
            activity['LF'] = min([act['LS'] for act in activities if act['name'] in activity['successors']])
        else:
            activity['LF'] = activity['EF']
        activity['LS'] = activity['LF'] - activity['duration']
            

    for activity in activities:
        activity['R'] = activity['LF'] - activity['EF']
        if activity['R'] == 0:
            activity['isCritical'] = True

    return jsonify(activities)

if __name__ == '__main__':
    app.run(debug=True)