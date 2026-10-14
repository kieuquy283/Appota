import argparse
import json

from src.service import answer_question


def main():
    parser = argparse.ArgumentParser(description="Query the synthetic Knowledge Guard backend")
    parser.add_argument("user_id", help="Synthetic user ID, e.g. U01")
    parser.add_argument("question")
    args = parser.parse_args()
    print(json.dumps(answer_question(args.user_id, args.question).to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
