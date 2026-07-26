import os
import webbrowser


def main():
    index_path = os.path.join(os.path.dirname(__file__), "electionPage", "index.html")
    webbrowser.open(f"file://{os.path.abspath(index_path)}")


if __name__ == "__main__":
    main()
