#!/usr/bin/env python
import os
import unicodedata

# from http://www.fileformat.info/info/unicode/block/general_punctuation/list.htm
UNICHAR_TABLE = [
  [ u'\u2000', 'EN QUAD (U+2000)', u' ' ],
  [ u'\u2001', 'EM QUAD (U+2001)', u' ' ],
  [ u'\u2002', 'EN SPACE (U+2002)', u' ' ],
  [ u'\u2003', 'EM SPACE (U+2003)', u' ' ],
  [ u'\u2004', 'THREE-PER-EM SPACE (U+2004)', u' ' ],
  [ u'\u2005', 'FOUR-PER-EM SPACE (U+2005)', u' ' ],
  [ u'\u2006', 'SIX-PER-EM SPACE (U+2006)', u' ' ],
  [ u'\u2007', 'FIGURE SPACE (U+2007)', u' ' ],
  [ u'\u2008', 'PUNCTUATION SPACE (U+2008)', u' ' ],
  [ u'\u2009', 'THIN SPACE (U+2009)', u' ' ],
  [ u'\u200A', 'HAIR SPACE (U+200A)', u' ' ],
  # [ u'\u200B', 'ZERO WIDTH SPACE (U+200B)', u'' ],
  # [ u'\u200C', 'ZERO WIDTH NON-JOINER (U+200C)', u'' ],
  # [ u'\u200D', 'ZERO WIDTH JOINER (U+200D)', u'' ],
  # [ u'\u200E', 'LEFT-TO-RIGHT MARK (U+200E)', u'' ],
  # [ u'\u200F', 'RIGHT-TO-LEFT MARK (U+200F)', u'' ],
  [ u'\u2010', 'HYPHEN (U+2010)', u'-' ],
  [ u'\u2011', 'NON-BREAKING HYPHEN (U+2011)', u'-' ],
  [ u'\u2012', 'FIGURE DASH (U+2012)', u'-' ],
  [ u'\u2013', 'EN DASH (U+2013)', u'-' ],
  [ u'\u2014', 'EM DASH (U+2014)', u'-' ],
  [ u'\u2015', 'HORIZONTAL BAR (U+2015)', u'-' ],
  [ u'\u2016', 'DOUBLE VERTICAL LINE (U+2016)', u'|' ],
  [ u'\u2017', 'DOUBLE LOW LINE (U+2017)', u'_' ],
  [ u'\u2018', 'LEFT SINGLE QUOTATION MARK (U+2018)', u"'" ],
  [ u'\u2019', 'RIGHT SINGLE QUOTATION MARK (U+2019)', u"'" ],
  [ u'\u201A', 'SINGLE LOW-9 QUOTATION MARK (U+201A)', u"'" ],
  [ u'\u201B', 'SINGLE HIGH-REVERSED-9 QUOTATION MARK (U+201B)', u"'" ],
  [ u'\u201C', 'LEFT DOUBLE QUOTATION MARK (U+201C)', u'""' ],
  [ u'\u201D', 'RIGHT DOUBLE QUOTATION MARK (U+201D)', u'""' ],
  [ u'\u201E', 'DOUBLE LOW-9 QUOTATION MARK (U+201E)', u'""' ],
  [ u'\u201F', 'DOUBLE HIGH-REVERSED-9 QUOTATION MARK (U+201F)', u'""' ],
  [ u'\u2020', 'DAGGER (U+2020)', u'+' ],
  [ u'\u2021', 'DOUBLE DAGGER (U+2021)', u'+' ],
  [ u'\u2022', 'BULLET (U+2022)', u'-' ],
  [ u'\u2023', 'TRIANGULAR BULLET (U+2023)', u'-' ],
  [ u'\u2024', 'ONE DOT LEADER (U+2024)', u'.' ],
  [ u'\u2025', 'TWO DOT LEADER (U+2025)', u'..' ],
  [ u'\u2026', 'HORIZONTAL ELLIPSIS (U+2026)', u'...' ],
  [ u'\u2027', 'HYPHENATION POINT (U+2027)', u'-' ],
  # [ u'\u2028', 'LINE SEPARATOR (U+2028)', u'' ],
  # [ u'\u2029', 'PARAGRAPH SEPARATOR (U+2029)', u'' ],
  # [ u'\u202A', 'LEFT-TO-RIGHT EMBEDDING (U+202A)', u'' ],
  # [ u'\u202B', 'RIGHT-TO-LEFT EMBEDDING (U+202B)', u'' ],
  # [ u'\u202C', 'POP DIRECTIONAL FORMATTING (U+202C)', u'' ],
  # [ u'\u202D', 'LEFT-TO-RIGHT OVERRIDE (U+202D)', u'' ],
  # [ u'\u202E', 'RIGHT-TO-LEFT OVERRIDE (U+202E)', u'' ],
  [ u'\u202F', 'NARROW NO-BREAK SPACE (U+202F)', u' ' ],
  # [ u'\u2030', 'PER MILLE SIGN (U+2030)', u'' ],
  # [ u'\u2031', 'PER TEN THOUSAND SIGN (U+2031)', u'' ],
  [ u'\u2032', 'PRIME (U+2032)', u"'" ],
  [ u'\u2033', 'DOUBLE PRIME (U+2033)', u"''" ],
  [ u'\u2034', 'TRIPLE PRIME (U+2034)', u"'''" ],
  [ u'\u2035', 'REVERSED PRIME (U+2035)', u'`' ],
  [ u'\u2036', 'REVERSED DOUBLE PRIME (U+2036)', u'`' ],
  [ u'\u2037', 'REVERSED TRIPLE PRIME (U+2037)', u'`' ],
  [ u'\u2038', 'CARET (U+2038)', u'^' ],
  [ u'\u2039', 'SINGLE LEFT-POINTING ANGLE QUOTATION MARK (U+2039)', u"'" ],
  [ u'\u203A', 'SINGLE RIGHT-POINTING ANGLE QUOTATION MARK (U+203A)', u"'" ],
  [ u'\u203B', 'REFERENCE MARK (U+203B)', u'#' ],
  [ u'\u203C', 'DOUBLE EXCLAMATION MARK (U+203C)', u'!!' ],
  # [ u'\u203D', 'INTERROBANG (U+203D)', u'' ],
  # [ u'\u203E', 'OVERLINE (U+203E)', u'' ],
  # [ u'\u203F', 'UNDERTIE (U+203F)', u'' ],
  # [ u'\u2040', 'CHARACTER TIE (U+2040)', u'' ],
  [ u'\u2041', 'CARET INSERTION POINT (U+2041)', u'^' ],
  # [ u'\u2042', 'ASTERISM (U+2042)', u'' ],
  [ u'\u2043', 'HYPHEN BULLET (U+2043)', u'-' ],
  [ u'\u2044', 'FRACTION SLASH (U+2044)', u'/' ],
  [ u'\u2045', 'LEFT SQUARE BRACKET WITH QUILL (U+2045)', u'[' ],
  [ u'\u2046', 'RIGHT SQUARE BRACKET WITH QUILL (U+2046)', u']' ],
  [ u'\u2047', 'DOUBLE QUESTION MARK (U+2047)', u'??' ],
  [ u'\u2048', 'QUESTION EXCLAMATION MARK (U+2048)', u'?!' ],
  [ u'\u2049', 'EXCLAMATION QUESTION MARK (U+2049)', u'!?' ],
  # [ u'\u204A', 'TIRONIAN SIGN ET (U+204A)', u'' ],
  # [ u'\u204B', 'REVERSED PILCROW SIGN (U+204B)', u'' ],
  [ u'\u204C', 'BLACK LEFTWARDS BULLET (U+204C)', u'-' ],
  [ u'\u204D', 'BLACK RIGHTWARDS BULLET (U+204D)', u'-' ],
  [ u'\u204E', 'LOW ASTERISK (U+204E)', u'*' ],
  [ u'\u204F', 'REVERSED SEMICOLON (U+204F)', u';' ],
  # [ u'\u2050', 'CLOSE UP (U+2050)', u'' ],
  [ u'\u2051', 'TWO ASTERISKS ALIGNED VERTICALLY (U+2051)', u'*' ],
  [ u'\u2052', 'COMMERCIAL MINUS SIGN (U+2052)', u'%' ],
  [ u'\u2053', 'SWUNG DASH (U+2053)', u'~' ],
  # [ u'\u2054', 'INVERTED UNDERTIE (U+2054)', u'' ],
  [ u'\u2055', 'FLOWER PUNCTUATION MARK (U+2055)', u'*' ],
  # [ u'\u2056', 'THREE DOT PUNCTUATION (U+2056)', u'' ],
  [ u'\u2057', 'QUADRUPLE PRIME (U+2057)', u"''''" ],
  # [ u'\u2058', 'FOUR DOT PUNCTUATION (U+2058)', u'' ],
  # [ u'\u2059', 'FIVE DOT PUNCTUATION (U+2059)', u'' ],
  [ u'\u205A', 'TWO DOT PUNCTUATION (U+205A)', u':' ],
  # [ u'\u205B', 'FOUR DOT MARK (U+205B)', u'' ],
  # [ u'\u205C', 'DOTTED CROSS (U+205C)', u'' ],
  # [ u'\u205D', 'TRICOLON (U+205D)', u'' ],
  # [ u'\u205E', 'VERTICAL FOUR DOTS (U+205E)', u'' ],
  [ u'\u205F', 'MEDIUM MATHEMATICAL SPACE (U+205F)', u' ' ]
  # [ u'\u2060', 'WORD JOINER (U+2060)', u'' ],
  # [ u'\u2061', 'FUNCTION APPLICATION (U+2061)', u'' ],
  # [ u'\u2062', 'INVISIBLE TIMES (U+2062)', u'' ],
  # [ u'\u2063', 'INVISIBLE SEPARATOR (U+2063)', u'' ],
  # [ u'\u2064', 'INVISIBLE PLUS (U+2064)', u'' ],
  # [ u'\u2066', 'LEFT-TO-RIGHT ISOLATE (U+2066)', u'' ],
  # [ u'\u2067', 'RIGHT-TO-LEFT ISOLATE (U+2067)', u'' ],
  # [ u'\u2068', 'FIRST STRONG ISOLATE (U+2068)', u'' ],
  # [ u'\u2069', 'POP DIRECTIONAL ISOLATE (U+2069)', u'' ],
  # [ u'\u206A', 'INHIBIT SYMMETRIC SWAPPING (U+206A)', u'' ],
  # [ u'\u206B', 'ACTIVATE SYMMETRIC SWAPPING (U+206B)', u'' ],
  # [ u'\u206C', 'INHIBIT ARABIC FORM SHAPING (U+206C)', u'' ],
  # [ u'\u206D', 'ACTIVATE ARABIC FORM SHAPING (U+206D)', u'' ],
  # [ u'\u206E', 'NATIONAL DIGIT SHAPES (U+206E)', u'' ],
  # [ u'\u206F', 'NOMINAL DIGIT SHAPES (U+206F)', u'' ],
]

UNICHAR_DICT = { }
for item in UNICHAR_TABLE:
  if item[2] != u'':
    UNICHAR_DICT[item[0]] = item[2] 

def toAscii(uchars):   
  uchars = unicode(unicodedata.normalize('NFKD', uchars))
  out = u''
  for c in uchars:
    if c in UNICHAR_DICT:
      out += UNICHAR_DICT[c]
    else:
      out += c
  return out.encode('ASCII', 'ignore')

if __name__ == '__main__':
  print(os.path.join('/test', '', ''))
  print(os.path.join('/test/', 'sub'))
  
  
