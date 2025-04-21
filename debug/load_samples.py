import requests, json

with open("debug/samples.json", "r") as file:
    samples = json.loads(
        s=file.read()
    )

    for query in samples['queries']:
        sample = samples['queries'][query]

        response = requests.post(
            url='http://localhost:8000/sample',
            json={
                'cypher': sample['query'],
                'tags': sample['keywords'],
                'description': sample['description'],
            },
        )

        print(response.json())
