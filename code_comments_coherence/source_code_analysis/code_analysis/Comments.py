# $ANTLR 3.1 Comments.g 2012-10-11 20:28:14

import sys
from antlr3 import *
from antlr3.compat import set, frozenset


# for convenience in actions
HIDDEN = BaseRecognizer.HIDDEN

# token types
RBRACK=14
APOS=39
BSLAHS=36
BACKQUOTE=28
STAR=20
LBRACK=13
EMARK=34
SHARP=35
PERCENT=27
LINE_COMMENT=6
LCURLY=29
MINUS=19
EOF=-1
SEMI=17
Identifier=9
LPAREN=11
AT=38
COLON=15
VBAR=22
QUOTE=40
RPAREN=12
GREATER=25
SLASH=21
WS=4
COMMA=16
AMPER=23
RCURLY=30
TILDE=32
ASSIGN=26
LESS=24
JavaIDDigit=8
PLUS=18
DIGIT=10
DOT=37
COMMENT=5
QMARK=33
Letter=7
CIRCUMFLEX=31


class Comments(Lexer):

    grammarFileName = "Comments.g"
    antlr_version = version_str_to_tuple("3.1")
    antlr_version_str = "3.1"

    def __init__(self, input=None, state=None):
        if state is None:
            state = RecognizerSharedState()
        Lexer.__init__(self, input, state)

        self.dfa5 = self.DFA5(
            self, 5,
            eot = self.DFA5_eot,
            eof = self.DFA5_eof,
            min = self.DFA5_min,
            max = self.DFA5_max,
            accept = self.DFA5_accept,
            special = self.DFA5_special,
            transition = self.DFA5_transition
            )


                      





    # $ANTLR start "WS"
    def mWS(self, ):

        try:
            _type = WS
            _channel = DEFAULT_CHANNEL

            # Comments.g:10:5: ( ( ' ' | '\\r' | '\\t' | '\\u000C' | '\\n' ) )
            # Comments.g:10:8: ( ' ' | '\\r' | '\\t' | '\\u000C' | '\\n' )
            pass 
            if (9 <= self.input.LA(1) <= 10) or (12 <= self.input.LA(1) <= 13) or self.input.LA(1) == 32:
                self.input.consume()
            else:
                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse

            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "WS"



    # $ANTLR start "COMMENT"
    def mCOMMENT(self, ):

        try:
            _type = COMMENT
            _channel = DEFAULT_CHANNEL

            # Comments.g:15:5: ( '/*' ( options {greedy=false; } : . )* '*/' )
            # Comments.g:15:9: '/*' ( options {greedy=false; } : . )* '*/'
            pass 
            self.match("/*")
            # Comments.g:15:14: ( options {greedy=false; } : . )*
            while True: #loop1
                alt1 = 2
                LA1_0 = self.input.LA(1)

                if (LA1_0 == 42) :
                    LA1_1 = self.input.LA(2)

                    if (LA1_1 == 47) :
                        alt1 = 2
                    elif ((0 <= LA1_1 <= 46) or (48 <= LA1_1 <= 65534)) :
                        alt1 = 1


                elif ((0 <= LA1_0 <= 41) or (43 <= LA1_0 <= 65534)) :
                    alt1 = 1


                if alt1 == 1:
                    # Comments.g:15:41: .
                    pass 
                    self.matchAny()


                else:
                    break #loop1


            self.match("*/")



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "COMMENT"



    # $ANTLR start "LINE_COMMENT"
    def mLINE_COMMENT(self, ):

        try:
            _type = LINE_COMMENT
            _channel = DEFAULT_CHANNEL

            # Comments.g:19:5: ( '//' (~ ( '\\n' | '\\r' ) )* ( '\\r' )? '\\n' )
            # Comments.g:19:7: '//' (~ ( '\\n' | '\\r' ) )* ( '\\r' )? '\\n'
            pass 
            self.match("//")
            # Comments.g:19:12: (~ ( '\\n' | '\\r' ) )*
            while True: #loop2
                alt2 = 2
                LA2_0 = self.input.LA(1)

                if ((0 <= LA2_0 <= 9) or (11 <= LA2_0 <= 12) or (14 <= LA2_0 <= 65534)) :
                    alt2 = 1


                if alt2 == 1:
                    # Comments.g:19:12: ~ ( '\\n' | '\\r' )
                    pass 
                    if (0 <= self.input.LA(1) <= 9) or (11 <= self.input.LA(1) <= 12) or (14 <= self.input.LA(1) <= 65534):
                        self.input.consume()
                    else:
                        mse = MismatchedSetException(None, self.input)
                        self.recover(mse)
                        raise mse



                else:
                    break #loop2


            # Comments.g:19:26: ( '\\r' )?
            alt3 = 2
            LA3_0 = self.input.LA(1)

            if (LA3_0 == 13) :
                alt3 = 1
            if alt3 == 1:
                # Comments.g:19:26: '\\r'
                pass 
                self.match(13)



            self.match(10)



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "LINE_COMMENT"



    # $ANTLR start "Identifier"
    def mIdentifier(self, ):

        try:
            _type = Identifier
            _channel = DEFAULT_CHANNEL

            # Comments.g:23:5: ( Letter ( Letter | JavaIDDigit )* )
            # Comments.g:23:9: Letter ( Letter | JavaIDDigit )*
            pass 
            self.mLetter()
            # Comments.g:23:16: ( Letter | JavaIDDigit )*
            while True: #loop4
                alt4 = 2
                LA4_0 = self.input.LA(1)

                if (LA4_0 == 36 or (48 <= LA4_0 <= 57) or (65 <= LA4_0 <= 90) or LA4_0 == 95 or (97 <= LA4_0 <= 122) or (192 <= LA4_0 <= 214) or (216 <= LA4_0 <= 246) or (248 <= LA4_0 <= 8191) or (12352 <= LA4_0 <= 12687) or (13056 <= LA4_0 <= 13183) or (13312 <= LA4_0 <= 15661) or (19968 <= LA4_0 <= 40959) or (63744 <= LA4_0 <= 64255)) :
                    alt4 = 1


                if alt4 == 1:
                    # Comments.g:
                    pass 
                    if self.input.LA(1) == 36 or (48 <= self.input.LA(1) <= 57) or (65 <= self.input.LA(1) <= 90) or self.input.LA(1) == 95 or (97 <= self.input.LA(1) <= 122) or (192 <= self.input.LA(1) <= 214) or (216 <= self.input.LA(1) <= 246) or (248 <= self.input.LA(1) <= 8191) or (12352 <= self.input.LA(1) <= 12687) or (13056 <= self.input.LA(1) <= 13183) or (13312 <= self.input.LA(1) <= 15661) or (19968 <= self.input.LA(1) <= 40959) or (63744 <= self.input.LA(1) <= 64255):
                        self.input.consume()
                    else:
                        mse = MismatchedSetException(None, self.input)
                        self.recover(mse)
                        raise mse



                else:
                    break #loop4


            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "Identifier"



    # $ANTLR start "Letter"
    def mLetter(self, ):

        try:
            # Comments.g:31:5: ( '\\u0024' | '\\u0041' .. '\\u005a' | '\\u005f' | '\\u0061' .. '\\u007a' | '\\u00c0' .. '\\u00d6' | '\\u00d8' .. '\\u00f6' | '\\u00f8' .. '\\u00ff' | '\\u0100' .. '\\u1fff' | '\\u3040' .. '\\u318f' | '\\u3300' .. '\\u337f' | '\\u3400' .. '\\u3d2d' | '\\u4e00' .. '\\u9fff' | '\\uf900' .. '\\ufaff' )
            # Comments.g:
            pass 
            if self.input.LA(1) == 36 or (65 <= self.input.LA(1) <= 90) or self.input.LA(1) == 95 or (97 <= self.input.LA(1) <= 122) or (192 <= self.input.LA(1) <= 214) or (216 <= self.input.LA(1) <= 246) or (248 <= self.input.LA(1) <= 8191) or (12352 <= self.input.LA(1) <= 12687) or (13056 <= self.input.LA(1) <= 13183) or (13312 <= self.input.LA(1) <= 15661) or (19968 <= self.input.LA(1) <= 40959) or (63744 <= self.input.LA(1) <= 64255):
                self.input.consume()
            else:
                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse





        finally:

            pass

    # $ANTLR end "Letter"



    # $ANTLR start "JavaIDDigit"
    def mJavaIDDigit(self, ):

        try:
            # Comments.g:48:5: ( '\\u0030' .. '\\u0039' | '\\u0660' .. '\\u0669' | '\\u06f0' .. '\\u06f9' | '\\u0966' .. '\\u096f' | '\\u09e6' .. '\\u09ef' | '\\u0a66' .. '\\u0a6f' | '\\u0ae6' .. '\\u0aef' | '\\u0b66' .. '\\u0b6f' | '\\u0be7' .. '\\u0bef' | '\\u0c66' .. '\\u0c6f' | '\\u0ce6' .. '\\u0cef' | '\\u0d66' .. '\\u0d6f' | '\\u0e50' .. '\\u0e59' | '\\u0ed0' .. '\\u0ed9' | '\\u1040' .. '\\u1049' )
            # Comments.g:
            pass 
            if (48 <= self.input.LA(1) <= 57) or (1632 <= self.input.LA(1) <= 1641) or (1776 <= self.input.LA(1) <= 1785) or (2406 <= self.input.LA(1) <= 2415) or (2534 <= self.input.LA(1) <= 2543) or (2662 <= self.input.LA(1) <= 2671) or (2790 <= self.input.LA(1) <= 2799) or (2918 <= self.input.LA(1) <= 2927) or (3047 <= self.input.LA(1) <= 3055) or (3174 <= self.input.LA(1) <= 3183) or (3302 <= self.input.LA(1) <= 3311) or (3430 <= self.input.LA(1) <= 3439) or (3664 <= self.input.LA(1) <= 3673) or (3792 <= self.input.LA(1) <= 3801) or (4160 <= self.input.LA(1) <= 4169):
                self.input.consume()
            else:
                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse





        finally:

            pass

    # $ANTLR end "JavaIDDigit"



    # $ANTLR start "DIGIT"
    def mDIGIT(self, ):

        try:
            _type = DIGIT
            _channel = DEFAULT_CHANNEL

            # Comments.g:65:7: ( '0' .. '9' )
            # Comments.g:65:9: '0' .. '9'
            pass 
            self.matchRange(48, 57)
            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "DIGIT"



    # $ANTLR start "LPAREN"
    def mLPAREN(self, ):

        try:
            _type = LPAREN
            _channel = DEFAULT_CHANNEL

            # Comments.g:67:11: ( '(' )
            # Comments.g:67:13: '('
            pass 
            self.match(40)
            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "LPAREN"



    # $ANTLR start "RPAREN"
    def mRPAREN(self, ):

        try:
            _type = RPAREN
            _channel = DEFAULT_CHANNEL

            # Comments.g:69:11: ( ')' )
            # Comments.g:69:13: ')'
            pass 
            self.match(41)
            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "RPAREN"



    # $ANTLR start "LBRACK"
    def mLBRACK(self, ):

        try:
            _type = LBRACK
            _channel = DEFAULT_CHANNEL

            # Comments.g:71:11: ( '[' )
            # Comments.g:71:13: '['
            pass 
            self.match(91)
            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "LBRACK"



    # $ANTLR start "RBRACK"
    def mRBRACK(self, ):

        try:
            _type = RBRACK
            _channel = DEFAULT_CHANNEL

            # Comments.g:73:11: ( ']' )
            # Comments.g:73:13: ']'
            pass 
            self.match(93)
            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "RBRACK"



    # $ANTLR start "COLON"
    def mCOLON(self, ):

        try:
            _type = COLON
            _channel = DEFAULT_CHANNEL

            # Comments.g:75:11: ( ':' )
            # Comments.g:75:13: ':'
            pass 
            self.match(58)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "COLON"



    # $ANTLR start "COMMA"
    def mCOMMA(self, ):

        try:
            _type = COMMA
            _channel = DEFAULT_CHANNEL

            # Comments.g:77:10: ( ',' )
            # Comments.g:77:12: ','
            pass 
            self.match(44)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "COMMA"



    # $ANTLR start "SEMI"
    def mSEMI(self, ):

        try:
            _type = SEMI
            _channel = DEFAULT_CHANNEL

            # Comments.g:79:9: ( ';' )
            # Comments.g:79:11: ';'
            pass 
            self.match(59)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "SEMI"



    # $ANTLR start "PLUS"
    def mPLUS(self, ):

        try:
            _type = PLUS
            _channel = DEFAULT_CHANNEL

            # Comments.g:81:9: ( '+' )
            # Comments.g:81:11: '+'
            pass 
            self.match(43)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "PLUS"



    # $ANTLR start "MINUS"
    def mMINUS(self, ):

        try:
            _type = MINUS
            _channel = DEFAULT_CHANNEL

            # Comments.g:83:10: ( '-' )
            # Comments.g:83:12: '-'
            pass 
            self.match(45)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "MINUS"



    # $ANTLR start "STAR"
    def mSTAR(self, ):

        try:
            _type = STAR
            _channel = DEFAULT_CHANNEL

            # Comments.g:85:9: ( '*' )
            # Comments.g:85:11: '*'
            pass 
            self.match(42)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "STAR"



    # $ANTLR start "SLASH"
    def mSLASH(self, ):

        try:
            _type = SLASH
            _channel = DEFAULT_CHANNEL

            # Comments.g:87:10: ( '/' )
            # Comments.g:87:12: '/'
            pass 
            self.match(47)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "SLASH"



    # $ANTLR start "VBAR"
    def mVBAR(self, ):

        try:
            _type = VBAR
            _channel = DEFAULT_CHANNEL

            # Comments.g:89:9: ( '|' )
            # Comments.g:89:11: '|'
            pass 
            self.match(124)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "VBAR"



    # $ANTLR start "AMPER"
    def mAMPER(self, ):

        try:
            _type = AMPER
            _channel = DEFAULT_CHANNEL

            # Comments.g:91:10: ( '&' )
            # Comments.g:91:12: '&'
            pass 
            self.match(38)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "AMPER"



    # $ANTLR start "LESS"
    def mLESS(self, ):

        try:
            _type = LESS
            _channel = DEFAULT_CHANNEL

            # Comments.g:93:9: ( '<' )
            # Comments.g:93:11: '<'
            pass 
            self.match(60)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "LESS"



    # $ANTLR start "GREATER"
    def mGREATER(self, ):

        try:
            _type = GREATER
            _channel = DEFAULT_CHANNEL

            # Comments.g:95:12: ( '>' )
            # Comments.g:95:14: '>'
            pass 
            self.match(62)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "GREATER"



    # $ANTLR start "ASSIGN"
    def mASSIGN(self, ):

        try:
            _type = ASSIGN
            _channel = DEFAULT_CHANNEL

            # Comments.g:97:11: ( '=' )
            # Comments.g:97:13: '='
            pass 
            self.match(61)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "ASSIGN"



    # $ANTLR start "PERCENT"
    def mPERCENT(self, ):

        try:
            _type = PERCENT
            _channel = DEFAULT_CHANNEL

            # Comments.g:99:12: ( '%' )
            # Comments.g:99:14: '%'
            pass 
            self.match(37)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "PERCENT"



    # $ANTLR start "BACKQUOTE"
    def mBACKQUOTE(self, ):

        try:
            _type = BACKQUOTE
            _channel = DEFAULT_CHANNEL

            # Comments.g:101:14: ( '`' )
            # Comments.g:101:16: '`'
            pass 
            self.match(96)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "BACKQUOTE"



    # $ANTLR start "LCURLY"
    def mLCURLY(self, ):

        try:
            _type = LCURLY
            _channel = DEFAULT_CHANNEL

            # Comments.g:103:11: ( '{' )
            # Comments.g:103:13: '{'
            pass 
            self.match(123)
            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "LCURLY"



    # $ANTLR start "RCURLY"
    def mRCURLY(self, ):

        try:
            _type = RCURLY
            _channel = DEFAULT_CHANNEL

            # Comments.g:105:11: ( '}' )
            # Comments.g:105:13: '}'
            pass 
            self.match(125)
            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "RCURLY"



    # $ANTLR start "CIRCUMFLEX"
    def mCIRCUMFLEX(self, ):

        try:
            _type = CIRCUMFLEX
            _channel = DEFAULT_CHANNEL

            # Comments.g:107:12: ( '^' )
            # Comments.g:107:14: '^'
            pass 
            self.match(94)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "CIRCUMFLEX"



    # $ANTLR start "TILDE"
    def mTILDE(self, ):

        try:
            _type = TILDE
            _channel = DEFAULT_CHANNEL

            # Comments.g:109:10: ( '~' )
            # Comments.g:109:12: '~'
            pass 
            self.match(126)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "TILDE"



    # $ANTLR start "QMARK"
    def mQMARK(self, ):

        try:
            _type = QMARK
            _channel = DEFAULT_CHANNEL

            # Comments.g:111:7: ( '?' )
            # Comments.g:111:9: '?'
            pass 
            self.match(63)
            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "QMARK"



    # $ANTLR start "EMARK"
    def mEMARK(self, ):

        try:
            _type = EMARK
            _channel = DEFAULT_CHANNEL

            # Comments.g:113:7: ( '!' )
            # Comments.g:113:9: '!'
            pass 
            self.match(33)
            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "EMARK"



    # $ANTLR start "SHARP"
    def mSHARP(self, ):

        try:
            _type = SHARP
            _channel = DEFAULT_CHANNEL

            # Comments.g:115:7: ( '#' )
            # Comments.g:115:9: '#'
            pass 
            self.match(35)
            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "SHARP"



    # $ANTLR start "BSLAHS"
    def mBSLAHS(self, ):

        try:
            _type = BSLAHS
            _channel = DEFAULT_CHANNEL

            # Comments.g:119:8: ( '\\\\' )
            # Comments.g:119:10: '\\\\'
            pass 
            self.match(92)
            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "BSLAHS"



    # $ANTLR start "DOT"
    def mDOT(self, ):

        try:
            _type = DOT
            _channel = DEFAULT_CHANNEL

            # Comments.g:121:5: ( '.' )
            # Comments.g:121:7: '.'
            pass 
            self.match(46)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "DOT"



    # $ANTLR start "AT"
    def mAT(self, ):

        try:
            _type = AT
            _channel = DEFAULT_CHANNEL

            # Comments.g:123:4: ( '@' )
            # Comments.g:123:6: '@'
            pass 
            self.match(64)
            #action start
            _channel = HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "AT"



    # $ANTLR start "APOS"
    def mAPOS(self, ):

        try:
            _type = APOS
            _channel = DEFAULT_CHANNEL

            # Comments.g:125:6: ( '\\'' )
            # Comments.g:125:8: '\\''
            pass 
            self.match(39)
            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "APOS"



    # $ANTLR start "QUOTE"
    def mQUOTE(self, ):

        try:
            _type = QUOTE
            _channel = DEFAULT_CHANNEL

            # Comments.g:127:7: ( '\"' )
            # Comments.g:127:9: '\"'
            pass 
            self.match(34)
            #action start
            _channel=HIDDEN
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "QUOTE"



    def mTokens(self):
        # Comments.g:1:8: ( WS | COMMENT | LINE_COMMENT | Identifier | DIGIT | LPAREN | RPAREN | LBRACK | RBRACK | COLON | COMMA | SEMI | PLUS | MINUS | STAR | SLASH | VBAR | AMPER | LESS | GREATER | ASSIGN | PERCENT | BACKQUOTE | LCURLY | RCURLY | CIRCUMFLEX | TILDE | QMARK | EMARK | SHARP | BSLAHS | DOT | AT | APOS | QUOTE )
        alt5 = 35
        alt5 = self.dfa5.predict(self.input)
        if alt5 == 1:
            # Comments.g:1:10: WS
            pass 
            self.mWS()


        elif alt5 == 2:
            # Comments.g:1:13: COMMENT
            pass 
            self.mCOMMENT()


        elif alt5 == 3:
            # Comments.g:1:21: LINE_COMMENT
            pass 
            self.mLINE_COMMENT()


        elif alt5 == 4:
            # Comments.g:1:34: Identifier
            pass 
            self.mIdentifier()


        elif alt5 == 5:
            # Comments.g:1:45: DIGIT
            pass 
            self.mDIGIT()


        elif alt5 == 6:
            # Comments.g:1:51: LPAREN
            pass 
            self.mLPAREN()


        elif alt5 == 7:
            # Comments.g:1:58: RPAREN
            pass 
            self.mRPAREN()


        elif alt5 == 8:
            # Comments.g:1:65: LBRACK
            pass 
            self.mLBRACK()


        elif alt5 == 9:
            # Comments.g:1:72: RBRACK
            pass 
            self.mRBRACK()


        elif alt5 == 10:
            # Comments.g:1:79: COLON
            pass 
            self.mCOLON()


        elif alt5 == 11:
            # Comments.g:1:85: COMMA
            pass 
            self.mCOMMA()


        elif alt5 == 12:
            # Comments.g:1:91: SEMI
            pass 
            self.mSEMI()


        elif alt5 == 13:
            # Comments.g:1:96: PLUS
            pass 
            self.mPLUS()


        elif alt5 == 14:
            # Comments.g:1:101: MINUS
            pass 
            self.mMINUS()


        elif alt5 == 15:
            # Comments.g:1:107: STAR
            pass 
            self.mSTAR()


        elif alt5 == 16:
            # Comments.g:1:112: SLASH
            pass 
            self.mSLASH()


        elif alt5 == 17:
            # Comments.g:1:118: VBAR
            pass 
            self.mVBAR()


        elif alt5 == 18:
            # Comments.g:1:123: AMPER
            pass 
            self.mAMPER()


        elif alt5 == 19:
            # Comments.g:1:129: LESS
            pass 
            self.mLESS()


        elif alt5 == 20:
            # Comments.g:1:134: GREATER
            pass 
            self.mGREATER()


        elif alt5 == 21:
            # Comments.g:1:142: ASSIGN
            pass 
            self.mASSIGN()


        elif alt5 == 22:
            # Comments.g:1:149: PERCENT
            pass 
            self.mPERCENT()


        elif alt5 == 23:
            # Comments.g:1:157: BACKQUOTE
            pass 
            self.mBACKQUOTE()


        elif alt5 == 24:
            # Comments.g:1:167: LCURLY
            pass 
            self.mLCURLY()


        elif alt5 == 25:
            # Comments.g:1:174: RCURLY
            pass 
            self.mRCURLY()


        elif alt5 == 26:
            # Comments.g:1:181: CIRCUMFLEX
            pass 
            self.mCIRCUMFLEX()


        elif alt5 == 27:
            # Comments.g:1:192: TILDE
            pass 
            self.mTILDE()


        elif alt5 == 28:
            # Comments.g:1:198: QMARK
            pass 
            self.mQMARK()


        elif alt5 == 29:
            # Comments.g:1:204: EMARK
            pass 
            self.mEMARK()


        elif alt5 == 30:
            # Comments.g:1:210: SHARP
            pass 
            self.mSHARP()


        elif alt5 == 31:
            # Comments.g:1:216: BSLAHS
            pass 
            self.mBSLAHS()


        elif alt5 == 32:
            # Comments.g:1:223: DOT
            pass 
            self.mDOT()


        elif alt5 == 33:
            # Comments.g:1:227: AT
            pass 
            self.mAT()


        elif alt5 == 34:
            # Comments.g:1:230: APOS
            pass 
            self.mAPOS()


        elif alt5 == 35:
            # Comments.g:1:235: QUOTE
            pass 
            self.mQUOTE()







    # lookup tables for DFA #5

    DFA5_eot = DFA.unpack(
        u"\2\uffff\1\44\42\uffff"
        )

    DFA5_eof = DFA.unpack(
        u"\45\uffff"
        )

    DFA5_min = DFA.unpack(
        u"\1\11\1\uffff\1\52\42\uffff"
        )

    DFA5_max = DFA.unpack(
        u"\1\ufaff\1\uffff\1\57\42\uffff"
        )

    DFA5_accept = DFA.unpack(
        u"\1\uffff\1\1\1\uffff\1\4\1\5\1\6\1\7\1\10\1\11\1\12\1\13\1\14\1"
        u"\15\1\16\1\17\1\21\1\22\1\23\1\24\1\25\1\26\1\27\1\30\1\31\1\32"
        u"\1\33\1\34\1\35\1\36\1\37\1\40\1\41\1\42\1\43\1\2\1\3\1\20"
        )

    DFA5_special = DFA.unpack(
        u"\45\uffff"
        )

            
    DFA5_transition = [
        DFA.unpack(u"\2\1\1\uffff\2\1\22\uffff\1\1\1\33\1\41\1\34\1\3\1\24"
        u"\1\20\1\40\1\5\1\6\1\16\1\14\1\12\1\15\1\36\1\2\12\4\1\11\1\13"
        u"\1\21\1\23\1\22\1\32\1\37\32\3\1\7\1\35\1\10\1\30\1\3\1\25\32\3"
        u"\1\26\1\17\1\27\1\31\101\uffff\27\3\1\uffff\37\3\1\uffff\u1f08"
        u"\3\u1040\uffff\u0150\3\u0170\uffff\u0080\3\u0080\uffff\u092e\3"
        u"\u10d2\uffff\u5200\3\u5900\uffff\u0200\3"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\42\4\uffff\1\43"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"")
    ]

    # class definition for DFA #5

    DFA5 = DFA
 



def main(argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    from antlr3.main import LexerMain
    main = LexerMain(Comments)
    main.stdin = stdin
    main.stdout = stdout
    main.stderr = stderr
    main.execute(argv)


if __name__ == '__main__':
    main(sys.argv)
