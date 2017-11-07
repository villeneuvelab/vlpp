var params= {
{% for tag, i in info.items() %}
    "{{tag}}": {
        "nbSlice": { 'Y':{{i.Y}} , 'Z':{{i.Z}} },
        "origin": { 'X': 98, 'Y': 134, 'Z':72 },
        "voxelSize": 1
    },
{% endfor %}
};
