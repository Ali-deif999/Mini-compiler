from Lexer.Lexer import Lexer


def main() -> None:
    source = 'x = 10\nlog: "Hello"\n'
    lexer = Lexer(source)

    for token in lexer.tokenize():
        print(token)


if __name__ == "__main__":
    main()
