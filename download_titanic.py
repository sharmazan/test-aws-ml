import requests

TITANIC_URL = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
OUTPUT_PATH = "titanic.csv"

def download_titanic_csv(url=TITANIC_URL, output_path=OUTPUT_PATH):
    response = requests.get(url)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"Downloaded Titanic dataset to {output_path}")

if __name__ == "__main__":
    download_titanic_csv()
