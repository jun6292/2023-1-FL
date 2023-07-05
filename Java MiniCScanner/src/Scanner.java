import java.io.*;

public class Scanner {

    private boolean isEof = false;
    private char ch = ' ';
    private BufferedReader input;
    private String line = "";
    private static int lineno = 0;
    private static int col = 1;
    private static int colnum = 1;  // 확장 구현
    private final String letters = "abcdefghijklmnopqrstuvwxyz"
        + "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    private final String digits = "0123456789";
    private final char eolnCh = '\n';
    private final char eofCh = '\004';
    

    public Scanner (String fileName) { // source filename
    	System.out.println("Begin scanning... programs/" + fileName + "\n");
        try {
            input = new BufferedReader (new FileReader(fileName));
        }
        catch (FileNotFoundException e) {
            System.out.println("File not found: " + fileName);
            System.exit(1);
        }
    }

    private char nextChar() { // Return next char
        if (ch == eofCh)
            error("Attempt to read past end of file");
        col++;
        if (col >= line.length()) {
            try {
                line = input.readLine( );
            } catch (IOException e) {
                System.err.println(e);
                System.exit(1);
            } // try
            if (line == null) // at end of file
                line = "" + eofCh;
            else {
                // System.out.println(lineno + ":\t" + line);
                lineno++;
                line += eolnCh;
            } // if line
            col = 0;
        } // if col
        return line.charAt(col);
    }
            

    public Token next( ) { // Return next token
        colnum = col + 1;   // 확장 구현
        do {
            if (isLetter(ch) || ch == '_') { // ident or keyword
                String spelling = concat(letters + digits + '_');
                return Token.keyword(spelling);
            } else if (isDigit(ch)) { // int literal
                // String number = concat(digits);
                String number = "";
                if (ch == '0') {    // 8진수일 때
                    number += ch;
                    ch = nextChar();
                    if (ch == 'x') {   // 16진수일 때
                        number += ch;
                        ch = nextChar();
                        number += concat(digits + "abcdef");
                    }
                    else if (ch == 'X') {
                        number += ch;
                        ch = nextChar();
                        number += concat(digits + "ABCDEF");
                    }
                    else {
                        if (isDigit(ch)) {
                            number += concat("01234567");
                        }
                    }
                    return Token.mkIntLiteral(number);
                }
                // return Token.mkIntLiteral(number);
                number = concat(digits);    // 10진수일 때
                if (ch != '.')  // .이 오지 않았다는 것은 int literal을 의미
                    return Token.mkIntLiteral(number);  // int literal 반환
                if (ch == '.')  {   // 123. 과 같은 숏폼 인식
                    number += ch;
                    ch = nextChar();
                    if (!isDigit(ch)) {
                        return Token.mkDoubleLiteral(number);
                    }
                    else {
                        String dnum = "";
                        dnum += concat(digits);
                        if (ch == 'e') {    // 지수부 표현
                            String fnum = "e";
                            ch = nextChar();
                            if (ch == '+' || ch == '-') {
                                fnum += ch;
                                ch = nextChar();
                            }
                            if (isDigit(ch)) {
                                fnum += concat(digits);
                                return Token.mkDoubleLiteral(number + dnum + fnum); // 부동 소수점 형식 반환
                            }
                        }
                        return Token.mkDoubleLiteral(number + dnum);    // 고정 소수점 형식 반환
                    }
                }        
            } else switch (ch) {
            case ' ': case '\t': case '\r': case eolnCh:
                ch = nextChar();
                colnum = col + 1;   // 확장 구현
                break;
            
            case '/':  // divide or divAssign or comment
                ch = nextChar();
                if (ch == '=')  { // divAssign
                	ch = nextChar();
                	return Token.divAssignTok;
                }
                
                // divide
                if (ch != '*' && ch != '/') return Token.divideTok;
                
                // multi line comment
                if (ch == '*') { 
                    ch = nextChar();
                    String str = "";
                    if (ch == '*')  // 확장4: multi line Documented comment -> /** 인식
                        ch = nextChar();
    				do {
    					while (ch != '*') {
                            str += ch;
                            ch = nextChar();
                        }
    					ch = nextChar();
                        if (ch != '/')  // *을 만났지만 다음 문자가 /가 아닌 경우 처리
                            str += "*";
    				} while (ch != '/');
                    // Documented Comments 내용 출력
                    System.out.println("\nDocumented Comments ------> " + str + '\n');
    				ch = nextChar();
                }
                // single line comment
                else if (ch == '/')  {
                    ch = nextChar();
                    String str = "";
                    if (ch == '/')  // 확장4: Single line Documented comment -> /// 인식
                        ch = nextChar();
                    while (ch != eolnCh) {
                        str += ch;
                        ch = nextChar();
                    }
                    // Documented Comments 내용 출력
                    System.out.println("\nDocumented Comments ------> " + str + '\n');
                    ch = nextChar();
	                // do {
	                //     ch = nextChar();
                    //     if (ch == '/')  
                    //         ch = nextChar()
	                // } while (ch != eolnCh);
	                // ch = nextChar();
                }
                
                break;

            // 확장3: char Literal 인식
            case '\'':  // 문자 앞의 '
                char ch1 = nextChar();
                // escape character '\' 처리 - 예시: '\n'
                String ec = "";
                if (ch1 == '\\') {
                    ec += ch1;  // \ 를 붙임
                    ch1 = nextChar();   // 'n'을 가져옴
                }
                if (nextChar() == '\'') {   // 문자 뒤의 '
                    ec += ch1;  // n 을 붙임
                    ch = nextChar();
                    return Token.mkCharLiteral(ec);
                }
                ch = nextChar();
                return Token.mkCharLiteral(ec); // Char Literal 반환

            // 확장3: String Literal 인식
            case '\"':
                String str = "";
                ch = nextChar();
                while (ch != '\"') {    // 문자열 끝의 "를 만날 때까지 반복
                    if (ch == '\\') {   // '\' 처리
                        str += ch;
                        ch = nextChar();
                        str += ch;
                        ch = nextChar();
                    }   
                    else {  // '\'가 아닐 때
                        str += ch;
                        ch = nextChar();
                    }
                }
                ch = nextChar();
                return Token.mkStringLiteral(str);  // String Literal 반환
            
            // 확장3: Double Literal 인식
            case '.':   // .123 과 같은 숏폼 인식
                String dnum = concat(digits);   // fixed point 실수 처리
                if (ch == 'e') {    // floating point 실수 처리, 지수부
                    ch = nextChar();
                    String fnum = "e";  
                    if (ch == '+' || ch == '-') {
                        fnum += ch;
                        ch = nextChar();
                    }
                    if (isDigit(ch)) {
                        fnum += concat(digits);
                        return Token.mkDoubleLiteral(dnum + fnum);  // 지수부 결합
                    }
                }
                return Token.mkDoubleLiteral(dnum);

            case eofCh: return Token.eofTok;
            
            case '+': 
            	ch = nextChar();
	            if (ch == '=')  { // addAssign
	            	ch = nextChar();
	            	return Token.addAssignTok;
	            }
	            else if (ch == '+')  { // increment
	            	ch = nextChar();
	            	return Token.incrementTok;
	            }
                return Token.plusTok;

            case '-': 
            	ch = nextChar();
                if (ch == '=')  { // subAssign
                	ch = nextChar();
                	return Token.subAssignTok;
                }
	            else if (ch == '-')  { // decrement
	            	ch = nextChar();
	            	return Token.decrementTok;
	            }
                return Token.minusTok;

            case '*': 
            	ch = nextChar();
                if (ch == '=')  { // multAssign
                	ch = nextChar();
                	return Token.multAssignTok;
                }
                return Token.multiplyTok;

            case '%': 
            	ch = nextChar();
                if (ch == '=')  { // remAssign
                	ch = nextChar();
                	return Token.remAssignTok;
                }
                return Token.reminderTok;

            case '(': ch = nextChar();
            return Token.leftParenTok;

            case ')': ch = nextChar();
            return Token.rightParenTok;

            case '{': ch = nextChar();
            return Token.leftBraceTok;

            case '}': ch = nextChar();
            return Token.rightBraceTok;

            // bubble.mc 소스 파일에 존재하는 토큰 '['를 인식하기 위해 추가
            case '[': ch = nextChar();		
            return Token.leftBracketTok;

            // bubble.mc 소스 파일에 존재하는 토큰 ']'를 인식하기 위해 추가
            case ']': ch = nextChar();	
            return Token.rightBracketTok;

            case ';': ch = nextChar();
            return Token.semicolonTok;

            // 확장2: 연산자 colon ':'을 인식하기 위해 추가
            case ':': ch = nextChar();
            return Token.colonTok;

            case ',': ch = nextChar();
            return Token.commaTok;
                
            case '&': check('&'); return Token.andTok;
            case '|': check('|'); return Token.orTok;

            case '=':
                return chkOpt('=', Token.assignTok,
                                   Token.eqeqTok);

            case '<':
                return chkOpt('=', Token.ltTok,
                                   Token.lteqTok);
            case '>': 
                return chkOpt('=', Token.gtTok,
                                   Token.gteqTok);
            case '!':
                return chkOpt('=', Token.notTok,
                                   Token.noteqTok);

            default:  error("Illegal character " + ch); 
            } // switch
        } while (true);
    } // next


    private boolean isLetter(char c) {
        return (c>='a' && c<='z' || c>='A' && c<='Z');
    }
  
    private boolean isDigit(char c) {
        return (c>='0' && c<='9');
    }

    private void check(char c) {
        ch = nextChar();
        if (ch != c) 
            error("Illegal character, expecting " + c);
        ch = nextChar();
    }

    private Token chkOpt(char c, Token one, Token two) {
        ch = nextChar();
        if (ch != c)
            return one;
        ch = nextChar();
        return two;
    }

    private String concat(String set) {
        String r = "";
        do {
            r += ch;
            ch = nextChar();
        } while (set.indexOf(ch) >= 0);
        return r;
    }

    public void error (String msg) {
        System.err.print(line);
        System.err.println("Error: column " + col + " " + msg);
        // 구현한 스캐너가 인식할 수 있는 토큰 구조에 해당하지 않는 경우에는 에러 메시지 출력 후 다음 토큰 인식 시도
        // System.exit(1);
    }

    static public void main ( String[] argv ) {
        Scanner lexer = new Scanner(argv[0]);
        Token tok = lexer.next( );
        while (tok != Token.eofTok) {
            // System.out.println(tok.toString());
            // 5. 추가 토큰 속성값을 출력 형식에 맞게 출력
            // Token -----> int (token number, token value, file name, line number, column number)
            System.out.print("Token -----> " + tok.value() + " (");
            System.out.print(tok.getTokNum() + ", " + tok.getTokVal() + ", ");
            System.out.print(argv[0] + ", " + lineno + ", " + colnum + ")\n");
            tok = lexer.next();
        } 
    } // main
}
