var registrationT1wTags = ["anattpl", "pettpl"];
var listSubject = [
{% for p in participants %}
{
    "id": {{loop.index - 1}},
    "text": "{{p.participant_id}}",
    "registrationsT1w": {
        "nbSlice": { 'X': {{p.X}}, 'Y':{{p.Y}} , 'Z':{{p.Z}} },
        "origin": { 'X': 98, 'Y': 134, 'Z':72 },
        "voxelSize": 1
    },
},
{% endfor %}
];
