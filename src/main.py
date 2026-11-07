from Lexer.Lexer import Lexer, LexerError
from Parser.Parser import Parser, ParserError


def main() -> None:
    source = 'x = 10 \nlog: "Hello"\n'
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse_program()
    except (LexerError, ParserError) as error:
        print(error)
        return


    print("Tokens:")
    for token in tokens:
        print(token)

    print("\nParsed Program:")
    print(program)


if __name__ == "__main__":
    main()

