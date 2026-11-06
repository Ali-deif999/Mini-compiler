from Lexer.Lexer import Lexer
from Parser.Parser import Parser


def main() -> None:
    source = 'x = 10\nlog: "Hello"\n'
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse_program()


    print("Tokens:")
    for token in tokens:
        print(token)

    print("\nParsed Program:")
    print(program)


if __name__ == "__main__":
    main()

