/** A Java 1.5 grammar for ANTLR v3 derived from the spec
 *
 *  This is a very close representation of the spec; the changes
 *  are comestic (remove left recursion) and also fixes (the spec
 *  isn't exactly perfect).  I have run this on the 1.4.2 source
 *  and some nasty looking enums from 1.5, but have not really
 *  tested for 1.5 compatibility.
 *
 *  I built this with: java -Xmx100M org.antlr.Tool java.g 
 *  and got two errors that are ok (for now):
 *  java.g:691:9: Decision can match input such as
 *    "'0'..'9'{'E', 'e'}{'+', '-'}'0'..'9'{'D', 'F', 'd', 'f'}"
 *    using multiple alternatives: 3, 4
 *  As a result, alternative(s) 4 were disabled for that input
 *  java.g:734:35: Decision can match input such as "{'$', 'A'..'Z',
 *    '_', 'a'..'z', '\u00C0'..'\u00D6', '\u00D8'..'\u00F6',
 *    '\u00F8'..'\u1FFF', '\u3040'..'\u318F', '\u3300'..'\u337F',
 *    '\u3400'..'\u3D2D', '\u4E00'..'\u9FFF', '\uF900'..'\uFAFF'}"
 *    using multiple alternatives: 1, 2
 *  As a result, alternative(s) 2 were disabled for that input
 *
 *  You can turn enum on/off as a keyword :)
 *
 *  Version 1.0 -- initial release July 5, 2006 (requires 3.0b2 or higher)
 *
 *  Primary author: Terence Parr, July 2006
 *
 *  Version 1.0.1 -- corrections by Koen Vanderkimpen & Marko van Dooren,
 *      October 25, 2006;
 *      fixed normalInterfaceDeclaration: now uses typeParameters instead
 *          of typeParameter (according to JLS, 3rd edition)
 *      fixed castExpression: no longer allows expression next to type
 *          (according to semantics in JLS, in contrast with syntax in JLS)
 *
 *  Version 1.0.2 -- Terence Parr, Nov 27, 2006
 *      java spec I built this from had some bizarre for-loop control.
 *          Looked weird and so I looked elsewhere...Yep, it's messed up.
 *          simplified.
 *
 *  Version 1.0.3 -- Chris Hogue, Feb 26, 2007
 *      Factored out an annotationName rule and used it in the annotation rule.
 *          Not sure why, but typeName wasn't recognizing references to inner
 *          annotations (e.g. @InterfaceName.InnerAnnotation())
 *      Factored out the elementValue section of an annotation reference.  Created 
 *          elementValuePair and elementValuePairs rules, then used them in the 
 *          annotation rule.  Allows it to recognize annotation references with 
 *          multiple, comma separated attributes.
 *      Updated elementValueArrayInitializer so that it allows multiple elements.
 *          (It was only allowing 0 or 1 element).
 *      Updated localVariableDeclaration to allow annotations.  Interestingly the JLS
 *          doesn't appear to indicate this is legal, but it does work as of at least
 *          JDK 1.5.0_06.
 *      Moved the Identifier portion of annotationTypeElementRest to annotationMethodRest.
 *          Because annotationConstantRest already references variableDeclarator which 
 *          has the Identifier portion in it, the parser would fail on constants in 
 *          annotation definitions because it expected two identifiers.  
 *      Added optional trailing ';' to the alternatives in annotationTypeElementRest.
 *          Wouldn't handle an inner interface that has a trailing ';'.
 *      Swapped the expression and type rule reference order in castExpression to 
 *          make it check for genericized casts first.  It was failing to recognize a
 *          statement like  "Class<Byte> TYPE = (Class<Byte>)...;" because it was seeing
 *          'Class<Byte' in the cast expression as a less than expression, then failing 
 *          on the '>'.
 *      Changed createdName to use typeArguments instead of nonWildcardTypeArguments.
 *          Again, JLS doesn't seem to allow this, but java.lang.Class has an example of
 *          of this construct.
 *      Changed the 'this' alternative in primary to allow 'identifierSuffix' rather than
 *          just 'arguments'.  The case it couldn't handle was a call to an explicit
 *          generic method invocation (e.g. this.<E>doSomething()).  Using identifierSuffix
 *          may be overly aggressive--perhaps should create a more constrained thisSuffix rule?
 *      
 *  Version 1.0.4 -- Hiroaki Nakamura, May 3, 2007
 *
 *  Fixed formalParameterDecls, localVariableDeclaration, forInit,
 *  and forVarControl to use variableModifier* not 'final'? (annotation)?
 *
 *  Version 1.0.5 -- Terence, June 21, 2007
 *  --a[i].foo didn't work. Fixed unaryExpression
 *
 *  Version 1.0.6 -- John Ridgway, March 17, 2008
 *      Made "assert" a switchable keyword like "enum".
 *      Fixed compilationUnit to disallow "annotation importDeclaration ...".
 *      Changed "Identifier ('.' Identifier)*" to "qualifiedName" in more 
 *          places.
 *      Changed modifier* and/or variableModifier* to classOrInterfaceModifiers,
 *          modifiers or variableModifiers, as appropriate.
 *      Renamed "bound" to "typeBound" to better match language in the JLS.
 *      Added "memberDeclaration" which rewrites to methodDeclaration or 
 *      fieldDeclaration and pulled type into memberDeclaration.  So we parse 
 *          type and then move on to decide whether we're dealing with a field
 *          or a method.
 *      Modified "constructorDeclaration" to use "constructorBody" instead of
 *          "methodBody".  constructorBody starts with explicitConstructorInvocation,
 *          then goes on to blockStatement*.  Pulling explicitConstructorInvocation
 *          out of expressions allowed me to simplify "primary".
 *      Changed variableDeclarator to simplify it.
 *      Changed type to use classOrInterfaceType, thus simplifying it; of course
 *          I then had to add classOrInterfaceType, but it is used in several 
 *          places.
 *      Fixed annotations, old version allowed "@X(y,z)", which is illegal.
 *      Added optional comma to end of "elementValueArrayInitializer"; as per JLS.
 *      Changed annotationTypeElementRest to use normalClassDeclaration and 
 *          normalInterfaceDeclaration rather than classDeclaration and 
 *          interfaceDeclaration, thus getting rid of a couple of grammar ambiguities.
 *      Split localVariableDeclaration into localVariableDeclarationStatement
 *          (includes the terminating semi-colon) and localVariableDeclaration.  
 *          This allowed me to use localVariableDeclaration in "forInit" clauses,
 *           simplifying them.
 *      Changed switchBlockStatementGroup to use multiple labels.  This adds an
 *          ambiguity, but if one uses appropriately greedy parsing it yields the
 *           parse that is closest to the meaning of the switch statement.
 *      Renamed "forVarControl" to "enhancedForControl" -- JLS language.
 *      Added semantic predicates to test for shift operations rather than other
 *          things.  Thus, for instance, the string "< <" will never be treated
 *          as a left-shift operator.
 *      In "creator" we rule out "nonWildcardTypeArguments" on arrayCreation, 
 *          which are illegal.
 *      Moved "nonWildcardTypeArguments into innerCreator.
 *      Removed 'super' superSuffix from explicitGenericInvocation, since that
 *          is only used in explicitConstructorInvocation at the beginning of a
 *           constructorBody.  (This is part of the simplification of expressions
 *           mentioned earlier.)
 *      Simplified primary (got rid of those things that are only used in
 *          explicitConstructorInvocation).
 *      Lexer -- removed "Exponent?" from FloatingPointLiteral choice 4, since it
 *          led to an ambiguity.
 *
 *      This grammar successfully parses every .java file in the JDK 1.5 source 
 *          tree (excluding those whose file names include '-', which are not
 *          valid Java compilation units).
 *
 *  Version 1.0.6.CD -- Peter Bulychev, April 25, 2008
 *	Small modifications for supporting Clone Digger
 *
 *  Version 1.0.6.1 -- Valerio Maggio, April 13, 2009
 *  Modified to be compatible with Parser and Lexer in Python
 *
 *  Known remaining problems:
 *      "Letter" and "JavaIDDigit" are wrong.  The actual specification of
 *      "Letter" should be "a character for which the method
 *      Character.isJavaIdentifierStart(int) returns true."  A "Java 
 *      letter-or-digit is a character for which the method 
 *      Character.isJavaIdentifierPart(int) returns true."
 *  
 */
grammar Java;
options {
    language=Python;
    k=2; 
    backtrack=true; 
    memoize=true;
    output=AST;
    ASTLabelType=CustomNode;
}

tokens {
    COMPILATION_UNIT;
    PACKAGE_DECLARATION;
    SINGLE_TYPE_IMPORT_DECLARATION;
    TYPE_IMPORT_ON_DEMAND_DECLARATION;
    SINGLE_STATIC_IMPORT_DECLARATION;
    STATIC_IMPORT_ON_DEMAND_DECLARATION;
    MODIFIERS;
    CLASS_DECLARATION;
    TYPE_PARAMETERS;
    TYPE_PARAMETER;
    TYPE_BOUND;
    ENUM_DECLARATION;
    ENUM_BODY;
    ENUM_CONSTANTS;
    ENUM_CONSTANT;
    ENUM_BODY_DECLARATIONS;
    INTERFACE_DECLARATION;
    CLASS_BODY;
    INTERFACE_BODY;
    STATIC_INITIALIZER;
    INSTANCE_INITIALIZER;
    VOID;
    FIELD_DECLARATION;
    METHOD_DECLARATION;
    ABSTRACT_METHOD_DECLARATION;
    CONSTRUCTOR_DECLARATION;
    VARIABLE_DECLARATOR;
    CONSTANT_DECLARATION;
    ARRAY_OF;
    ARRAY_INITIALIZER;
    CONSTRUCTOR_BODY;
    INSTANTIATION;
    SELECT;
    TYPE_ARGUMENTS;
    WILDCARD;
    FORMAL_PARAMETERS;
    FORMAL_PARAMETER;
    LAST_FORMAL_PARAMETER;
    ALTERNATE_CONSTRUCTOR_INVOCATION;
    UNQUALIFIED_SUPERCLASS_CONSTRUCTOR_INVOCATION;
    QUALIFIED_SUPERCLASS_CONSTRUCTOR_INVOCATION;
    NORMAL_ANNOTATION;
    SINGLE_ELEMENT_ANNOTATION;
    MARKER_ANNOTATION;
    ELEMENT_VALUE_PAIR;
    ELEMENT_VALUE_ARRAY_INITIALIZER;
    ANNOTATION_INTERFACE;
    ANNOTATION_TYPE_BODY;
    ANNOTATION_METHOD;
    BLOCK;
    LOCAL_VARIABLE_DECLARATION;
    ASSERT_STATEMENT;
    EMPTY_STATEMENT;
    EXPRESSION_STATEMENT;
    SWITCH_BLOCK_STATEMENT_GROUP;
    BASIC_FOR_CONTROL;
    FOR_INIT_DECLARATION;
    FOR_INIT_EXPRESSION_LIST;
    ENHANCED_FOR_CONTROL;
    FOR_UPDATE;
    EXPRESSION_LIST;
    LEFT_SHIFT_ASSIGN;
    UNSIGNED_RIGHT_SHIFT_ASSIGN;
    SIGNED_RIGHT_SHIFT_ASSIGN;
    LESS_THAN_OR_EQUAL_TO;
    GREATER_THAN_OR_EQUAL_TO;
    LEFT_SHIFT;
    UNSIGNED_RIGHT_SHIFT;
    SIGNED_RIGHT_SHIFT;
    PREFIX_EXPRESSION;
    POST_INCREMENT_EXPRESSION;
    POST_DECREMENT_EXPRESSION;
    CAST;
    THIS;
    UNQUALIFIED_SUPER;
    CLASS_DESIGNATOR;
    ARRAY_ACCESS;
    CALL;
    QUALIFIED_THIS;
    QUALIFIED_SUPER;
    UNQUALIFIED_CLASS_INSTANCE_CREATION;
    QUALIFIED_CLASS_INSTANCE_CREATION;
    NEW_INITIALIZED_ARRAY;
    NEW_ARRAY;
    EXPLICIT_GENERIC_INVOCATIONS;
    NON_WILD_TYPE_ARGUMENTS;
    INNER_THIS;
    ARGUMENTS;
    METHOD_BODY;
}

@lexer::init {
  self.enumIsKeyword = False;
  self.assertIsKeyword = True;
}

// starting point for parsing a java file
/* The annotations are separated out to make parsing faster, but must be associated with
   a packageDeclaration or a typeDeclaration (and not an empty one). */
compilationUnit
    :   ('@')=> annotations
        (   packageDeclaration[$annotations.tree] importDeclaration* typeDeclaration*
            -> ^(COMPILATION_UNIT packageDeclaration importDeclaration* typeDeclaration*)
        |   classOrInterfaceDeclaration[$annotations.tree] typeDeclaration*
            -> ^(COMPILATION_UNIT classOrInterfaceDeclaration typeDeclaration*)
       )
    |   (packageDeclaration[None])? importDeclaration* typeDeclaration*
        -> ^(COMPILATION_UNIT packageDeclaration? importDeclaration* typeDeclaration*)
    ;

packageDeclaration[annotations]
@after {retval.tree.instruction_class = "KEYWORD"; retval.tree.instruction = "PACKAGE_KEYWORD"}
    :   'package' qualifiedName ';'
        -> ^(PACKAGE_DECLARATION {annotations} qualifiedName)
    ;
    
importDeclaration
@after {retval.tree.instruction_class = "KEYWORD"; retval.tree.instruction = "IMPORT_KEYWORD"}
    :   'import' (staticModifier='static')? qualifiedName ('.' wildcard='*')? ';'
        -> {staticModifier == None and wildcard == None}?
            ^(SINGLE_TYPE_IMPORT_DECLARATION qualifiedName)
        -> {staticModifier == None and wildcard != None}?
            ^(TYPE_IMPORT_ON_DEMAND_DECLARATION qualifiedName)
        -> {staticModifier != None and wildcard == None}?
            ^(SINGLE_STATIC_IMPORT_DECLARATION qualifiedName)
        -> /*{staticModifier != None and wildcard != None}? */
            ^(STATIC_IMPORT_ON_DEMAND_DECLARATION qualifiedName)
    ;
    
typeDeclaration
    :   classOrInterfaceDeclaration[None]
    |   ';'
        ->
    ;
    
classOrInterfaceDeclaration[annotations]
    :   classOrInterfaceModifiers[annotations]! (classDeclaration[$classOrInterfaceModifiers.tree] | interfaceDeclaration[$classOrInterfaceModifiers.tree])
    ;
    
classOrInterfaceModifiers[annotations]
    :   classOrInterfaceModifier*
        -> ^(MODIFIERS {annotations} classOrInterfaceModifier*)
    ;

classOrInterfaceModifier
    :   annotation     // class or interface
    |   public_mod     // class or interface
    |   protected_mod  // class or interface
    |   private_mod    // class or interface
    |   abstract_mod   // class or interface
    |   static_mod     // class or interface
    |   final_mod      // class only -- does not apply to interfaces
    |   strictfp_mod   // class or interface
    ;

modifiers
    :   modifier*
        -> ^(MODIFIERS modifier*)
    ;

classDeclaration[modifiers]
    :   normalClassDeclaration[modifiers]
    |   enumDeclaration[modifiers]
    ;
    
normalClassDeclaration[modifiers]
@after {retval.tree.is_statement = True; retval.tree.is_class_statement = True; \
        retval.tree.instruction_class = "CLASS_DECLARATION"; retval.tree.instruction = "CLASS_KEYWORD";}
    :   'class' identifier (typeParameters)?
        (extendsPhrase)?
        (implementsPhrase)?
        classBody
        -> ^(CLASS_DECLARATION {modifiers} identifier typeParameters? extendsPhrase? implementsPhrase? classBody)
    ;

extendsPhrase
@after {retval.tree.instruction_class = "KEYWORD"; retval.tree.instruction = "INHERITANCE_KEYWORD"}
    :   'extends' type
        -> ^('extends' type)
    ;

implementsPhrase
@after {retval.tree.instruction_class = "KEYWORD"; retval.tree.instruction = "INTERFACE_IMPLEMENTATION_KEYWORD"}
    :   'implements' typeList
        -> ^('implements' typeList)
    ;

typeParameters
    :   '<' typeParameter (',' typeParameter)* '>'
        -> ^(TYPE_PARAMETERS typeParameter+)
    ;

typeParameter
    :   identifier ('extends' typeBound)?
        -> ^(TYPE_PARAMETER identifier typeBound?)
    ;
        
typeBound
    :   type ('&' type)*
        -> ^(TYPE_BOUND type+)
    ;

enumDeclaration[modifiers]
@after {retval.tree.is_statement = True; retval.tree.is_class_statement = True;\
        retval.tree.instruction_class = "CLASS_DECLARATION"; retval.tree.instruction = "ENUM_CLASS_KEYWORD";}
    :   'enum' identifier (implementsPhrase)? enumBody
        -> ^(ENUM_DECLARATION {modifiers} identifier implementsPhrase? enumBody)
    ;

enumBody
    :   '{' enumConstants? ','? enumBodyDeclarations? '}'
        -> ^(ENUM_BODY enumConstants? enumBodyDeclarations?)
    ;

enumConstants
    :   enumConstant (',' enumConstant)*
        -> ^(ENUM_CONSTANTS enumConstant+)
    ;
    
enumConstant
    :   annotations? identifier (arguments)? (classBody)?
        -> ^(ENUM_CONSTANT annotations? identifier arguments? classBody?)
    ;
    
enumBodyDeclarations
    :   ';' (classBodyDeclaration)*
        -> ^(ENUM_BODY_DECLARATIONS classBodyDeclaration*)
    ;
    
interfaceDeclaration[modifiers]
    :   normalInterfaceDeclaration[modifiers]
    |   annotationTypeDeclaration[modifiers]
    ;
    
normalInterfaceDeclaration[modifiers]
@after {retval.tree.is_statement = True; retval.tree.is_class_statement = True;\
        retval.tree.instruction_class = "CLASS_DECLARATION"; retval.tree.instruction = "INTERFACE_KEYWORD";}
    :   'interface' identifier typeParameters? (extendsInterfaces)? interfaceBody
        -> ^(INTERFACE_DECLARATION {modifiers} identifier typeParameters? extendsInterfaces? interfaceBody)
    ;

extendsInterfaces
@after {retval.tree.instruction_class = "KEYWORD"; retval.tree.instruction = "INHERITANCE_KEYWORD"}
    :   'extends' typeList
        -> ^('extends' typeList)
    ;
    
typeList
    :   type (','! type)*
    ;
    
classBody
    :   '{' classBodyDeclaration* '}'
        -> ^(CLASS_BODY classBodyDeclaration*)
    ;
    
interfaceBody
    :   '{' interfaceBodyDeclaration* '}'
        -> ^(INTERFACE_BODY interfaceBodyDeclaration*)
    ;

classBodyDeclaration
    :   ';'
        ->
    |   'static' block
        -> ^(STATIC_INITIALIZER block)
    |   block
        -> ^(INSTANCE_INITIALIZER block)
    |   modifiers! memberDecl[$modifiers.tree]
    ;
    
memberDecl[modifiers]
    :   genericMethodOrConstructorDecl[modifiers]
    |   memberDeclaration[modifiers]
    |   'void' identifier voidMethodDeclaratorRest[modifiers, $identifier.tree]
        -> voidMethodDeclaratorRest
    |   identifier constructorDeclaratorRest[modifiers, None, $identifier.tree]
        -> constructorDeclaratorRest
    |   interfaceDeclaration[modifiers]
    |   classDeclaration[modifiers]
    ;
    
memberDeclaration[modifiers]
    :   type! (methodDeclaration[modifiers, $type.tree]
              | fieldDeclaration[modifiers, $type.tree])
    ;

genericMethodOrConstructorDecl[modifiers]
    :   typeParameters! genericMethodOrConstructorRest[modifiers, $typeParameters.tree]
    ;
    
genericMethodOrConstructorRest[modifiers, typeParameters]
    :   rt=resultType! identifier! 
        methodDeclaratorRest[modifiers, typeParameters, $rt.tree, $identifier.tree]
    |   identifier! constructorDeclaratorRest[modifiers, typeParameters, $identifier.tree]
    ;

resultType 
    :   type
    |   'void' -> VOID
    ;

methodDeclaration[modifiers, returnType]
    :   identifier! methodDeclaratorRest[modifiers, returnType, None, $identifier.tree]
    ;

fieldDeclaration[modifiers, fieldType]
@after {retval.tree.is_statement = True;}
    :   variableDeclarators ';'
        -> ^(FIELD_DECLARATION {modifiers} {fieldType} variableDeclarators)
    ;
        
interfaceBodyDeclaration
    :   modifiers! interfaceMemberDecl[$modifiers.tree]
    |   ';'!
    ;

interfaceMemberDecl[modifiers]
    :   interfaceMethodOrFieldDecl[modifiers]
    |   interfaceGenericMethodDecl[modifiers]
    |   'void'! identifier! voidInterfaceMethodDeclaratorRest[modifiers, $identifier.tree]
    |   interfaceDeclaration[ modifiers]
    |   classDeclaration[modifiers]
    ;
    
interfaceMethodOrFieldDecl[modifiers]
    :   t=type! identifier! interfaceMethodOrFieldRest[modifiers, t.tree, $identifier.tree]
    ;
    
interfaceMethodOrFieldRest[modifiers, type, identifier]
    :   constantDeclaratorsRest[modifiers, type, identifier] ';'!
    |   interfaceMethodDeclaratorRest[modifiers, None, type, identifier]
    ;

/* This converts obsolete post-formal '[]' array specifiers to array specifiers on the
   return type in the AST. */    
methodDeclaratorRest[modifiers, type, typeParameters, identifier]
@after {retval.tree.is_statement = True; retval.tree.is_method_statement = True;\
        retval.tree.instruction_class = "METHOD_DECLARATION"; retval.tree.instruction = "METHOD_DECLARATION";}
    :   formalParameters 
        ( '[' ']'
          { type = adaptor.becomeRoot(adaptor.createFromType(ARRAY_OF, "ARRAY_OF"), type) }
        )*
        (throwsPhrase)?
        (  methodBody
            -> ^(METHOD_DECLARATION {modifiers} {$type} {typeParameters} {identifier}
                 formalParameters (throwsPhrase)? methodBody)
        |   ';'
            -> ^(METHOD_DECLARATION {modifiers} {$type} {typeParameters} {identifier}
                 formalParameters (throwsPhrase)?)
        )
    ;

throwsPhrase
    :   'throws' qualifiedNameList -> ^('throws' qualifiedNameList)
    ;
    
voidMethodDeclaratorRest[modifiers, identifier]
@after {retval.tree.is_statement = True; retval.tree.is_method_statement = True;\
        retval.tree.instruction_class = "METHOD_DECLARATION"; retval.tree.instruction = "METHOD_DECLARATION";}
    :   formalParameters (throwsPhrase)?
        (  methodBody
            -> ^(METHOD_DECLARATION {modifiers} VOID {identifier} formalParameters 
                (throwsPhrase)? methodBody)
        |   ';'
            -> ^(METHOD_DECLARATION {modifiers} VOID {identifier} formalParameters 
                (throwsPhrase)?)
       )
    ;
    
interfaceMethodDeclaratorRest[modifiers, typeParameters, type, identifier]
@after {retval.tree.is_statement = True; retval.tree.is_method_statement = True;\
        retval.tree.instruction_class ="METHOD_DECLARATION"; retval.tree.instruction = "INTERFACE_METHOD_DECLARATION";}
    :   formalParameters 
        ('[' ']'
            { type = adaptor.becomeRoot(adaptor.createFromType(ARRAY_OF, "ARRAY_OF"), type) })*
        (throwsPhrase)? ';'
        -> ^(ABSTRACT_METHOD_DECLARATION {modifiers} {typeParameters} {type} {identifier} formalParameters (throwsPhrase)?)
    ;
    
interfaceGenericMethodDecl[modifiers]
    :   typeParameters! rt=resultType! identifier!
        interfaceMethodDeclaratorRest[modifiers, $typeParameters.tree, rt.tree, $identifier.tree]
    ;
    
voidInterfaceMethodDeclaratorRest[modifiers, identifier]
@after {retval.tree.is_statement = True; retval.tree.is_method_statement = True;\
        retval.tree.instruction_class = "METHOD_DECLARATION"; retval.tree.instruction = "INTERFACE_METHOD_DECLARATION";}
    :   formalParameters (throwsPhrase)? ';'
        -> ^(ABSTRACT_METHOD_DECLARATION {modifiers} VOID {identifier} formalParameters (throwsPhrase)?)
    ;
    
constructorDeclaratorRest[modifiers, typeParameters, identifier]
@after {retval.tree.is_statement = True; retval.tree.is_method_statement = True;\
        retval.tree.instruction_class = "METHOD_DECLARATION"; retval.tree.instruction = "CONSTRUCTOR_METHOD_DECLARATION";}
    :   formalParameters (throwsPhrase)? constructorBody
        -> ^(CONSTRUCTOR_DECLARATION {modifiers} {typeParameters} {identifier}
             formalParameters (throwsPhrase)? constructorBody)
    ;

constantDeclarator[modifiers, type]
    :   identifier! constantDeclaratorRest[modifiers, type, $identifier.tree]
    ;
    
variableDeclarators
    :   variableDeclarator (',' variableDeclarator)*
        -> variableDeclarator+
    ;

variableDeclarator
    :   variableDeclaratorId ('=' variableInitializer)?
        -> ^(VARIABLE_DECLARATOR variableDeclaratorId variableInitializer?)
    ;
    
constantDeclaratorsRest[modifiers, type, identifier]
    :   constantDeclaratorRest[modifiers, type, identifier] (','! constantDeclarator[modifiers, type])*
    ;

constantDeclaratorRest[modifiers, type, identifier]
    :   ('[' ']'
            { type = adaptor.becomeRoot(adaptor.createFromType(ARRAY_OF, "ARRAY_OF"), type); })*
        '=' variableInitializer
        -> ^(CONSTANT_DECLARATION {modifiers} {type} {identifier} variableInitializer)
        ;
    
variableDeclaratorId
    :   (identifier -> identifier) 
        ('[' ']' -> ^(ARRAY_OF $variableDeclaratorId) )*
    ;

variableInitializer
    :   arrayInitializer
    |   expression
    ;
        
arrayInitializer
    :   '{' (variableInitializer (',' variableInitializer)* (',')? )? '}'
        -> ^(ARRAY_INITIALIZER variableInitializer*)
    ;

modifier
    :   annotation
    |   public_mod
    |   protected_mod
    |   private_mod
    |   static_mod
    |   abstract_mod
    |   final_mod
    |   native_mod
    |   synchronized_mod
    |   transient_mod
    |   volatile_mod
    |   strictfp_mod
    ;

packageOrTypeName
    :   qualifiedName
    ;

enumConstantName
    :   identifier
    ;

typeName
    :   qualifiedName
    ;

// 4.1 -- The Kinds of Types and Values
type
	:	( classOrInterfaceType -> classOrInterfaceType )
        ( '[' ']' -> ^(ARRAY_OF $type) )*
	|	( primitiveType -> primitiveType )
        ( '[' ']' -> ^(ARRAY_OF $type) )*
	;

classOrInterfaceType
@after {retval.tree.instruction_class = "TYPE"; retval.tree.instruction = "CLASS_OR_INTERFACE_TYPE"}
	:	( identifier -> identifier )
        ( typeArguments -> ^(INSTANTIATION $classOrInterfaceType typeArguments) )?
        ( ( '.' identifier -> ^(SELECT $classOrInterfaceType identifier) )
          (typeArguments -> ^(INSTANTIATION $classOrInterfaceType typeArguments) )? 
        )*
	;

primitiveType
@after {retval.tree.instruction_class = "TYPE"; retval.tree.instruction = "PRIMITIVE_TYPE"}
    :   'boolean'
    |   'char'
    |   'byte'
    |   'short'
    |   'int'
    |   'long'
    |   'float'
    |   'double'
    ;

variableModifier
    :   final_mod
    |   annotation
    ;

typeArguments
    :   '<' typeArgument (',' typeArgument)* '>'
        -> ^(TYPE_ARGUMENTS typeArgument+)
    ;
    
typeArgument
    :   type
        -> type
    |   '?' ((kind='extends' | kind='super') type)?
        -> ^(WILDCARD $kind? type?)
    ;
    
qualifiedNameList
    :   qualifiedName (','! qualifiedName)*
    ;

formalParameters
    :   '(' formalParameterDecls? ')'
        -> ^(FORMAL_PARAMETERS formalParameterDecls?)
    ;
    
formalParameterDecls
    :   variableModifiers! pType=type! formalParameterDeclsRest[$variableModifiers.tree, pType.tree]
    ;
    
formalParameterDeclsRest[modifiers, type]
    :   variableDeclaratorId 
        (',' formalParameterDecls
            -> ^(FORMAL_PARAMETER {modifiers} {type} variableDeclaratorId) formalParameterDecls
        |
            -> ^(FORMAL_PARAMETER {modifiers} {type} variableDeclaratorId)
        )
    |   '...' variableDeclaratorId
        -> ^(LAST_FORMAL_PARAMETER {modifiers} {type} variableDeclaratorId)
    ;
    
methodBody
@after {retval.tree.is_statement = True}
    :   '{' blockStatement* '}'
        -> ^(METHOD_BODY blockStatement*)
    ;
    

constructorBody
@after {retval.tree.is_statement = True}
    :   '{' explicitConstructorInvocation? blockStatement* '}'
        -> ^(CONSTRUCTOR_BODY explicitConstructorInvocation? blockStatement*)
    ;

explicitConstructorInvocation
    :   (nonWildcardTypeArguments)?
        ( ( 'this' arguments ';' 
            -> ^(ALTERNATE_CONSTRUCTOR_INVOCATION nonWildcardTypeArguments? arguments) )
        | ( 'super' arguments ';'
            -> ^(UNQUALIFIED_SUPERCLASS_CONSTRUCTOR_INVOCATION nonWildcardTypeArguments? arguments) )
        )
    |   primary '.' nonWildcardTypeArguments? 'super' arguments ';'
        -> ^(QUALIFIED_SUPERCLASS_CONSTRUCTOR_INVOCATION primary nonWildcardTypeArguments? arguments)
    ;


qualifiedName
    :   (identifier->identifier)
        ('.' identifier -> ^(SELECT $qualifiedName identifier))*
    ;
    
literal
    :   integerLiteral
    |   floatingPointLiteral
    |   characterLiteral
    |   stringLiteral
    |   booleanLiteral
    |   nullLiteral
    ;

integerLiteral
@after {retval.tree.instruction_class = "LITERAL"; retval.tree.instruction = "INTEGER_LITERAL"}
    :   HexLiteral
    |   OctalLiteral
    |   DecimalLiteral
    ;

booleanLiteral
@after {retval.tree.instruction_class = "LITERAL"; retval.tree.instruction = "BOOLEAN_LITERAL"}
    :   'true'
    |   'false'
    ;

floatingPointLiteral
@after {retval.tree.instruction_class = "LITERAL"; retval.tree.instruction = "FLOATING_POINT_LITERAL"}
    :   FloatingPointLiteral
    ;

characterLiteral
@after {retval.tree.instruction_class = "LITERAL"; retval.tree.instruction = "CHARACTER_LITERAL"}
    :   CharacterLiteral
    ;

stringLiteral
@after {retval.tree.instruction_class = "LITERAL"; retval.tree.instruction = "STRING_LITERAL"}
    :   StringLiteral
    ;

nullLiteral
@after {retval.tree.instruction_class = "LITERAL"; retval.tree.instruction = "NULL_LITERAL"}    
    :   'null'
    ;

// ANNOTATIONS

annotations
    :   annotation+
    ;

annotation
    :   '@' annotationName 
        ( '(' ( elementValuePairs
                -> ^(NORMAL_ANNOTATION annotationName elementValuePairs)
              | elementValue 
                -> ^(SINGLE_ELEMENT_ANNOTATION annotationName elementValue)
              )? 
          ')'
        | // Nothing
          -> ^(MARKER_ANNOTATION annotationName)
        )
    ;
    
annotationName
    :   (identifier -> identifier)
        ('.' id=identifier -> ^(SELECT $annotationName $id))*
    ;

elementValuePairs
    :   elementValuePair (',' elementValuePair)*
        -> elementValuePair+
    ;

elementValuePair
    :   identifier '=' elementValue
        -> ^(ELEMENT_VALUE_PAIR identifier elementValue)
    ;
    
elementValue
    :   conditionalExpression
    |   annotation
    |   elementValueArrayInitializer
    ;
    
elementValueArrayInitializer
    :   '{' (elementValue (',' elementValue)*)? (',')? '}'
        -> ^(ELEMENT_VALUE_ARRAY_INITIALIZER elementValue+)
    ;
    
annotationTypeDeclaration[modifiers]
@after {retval.tree.is_statement = True; retval.tree.is_class_statement = True;\
        retval.tree.instruction_class = "CLASS_DECLARATION"; retval.tree.instruction = "ANNOTATION_DECLARATION";}
    :   '@' 'interface' identifier annotationTypeBody
        -> ^(ANNOTATION_INTERFACE {modifiers} identifier annotationTypeBody)
    ;
    
annotationTypeBody
    :   '{' (annotationTypeElementDeclaration)* '}'
        -> ^(ANNOTATION_TYPE_BODY annotationTypeElementDeclaration*)
    ;
    
annotationTypeElementDeclaration
    :   modifiers! annotationTypeElementRest[$modifiers.tree]
    ;
    
annotationTypeElementRest[modifiers]
    :   type annotationMethodOrConstantRest[modifiers, $type.tree] ';'
        -> annotationMethodOrConstantRest
    |   normalClassDeclaration[modifiers] ';'!?
    |   normalInterfaceDeclaration[modifiers] ';'!?
    |   enumDeclaration[modifiers] ';'!?
    |   annotationTypeDeclaration[modifiers] ';'!?
    ;
    
annotationMethodOrConstantRest[modifiers, type]
    :   annotationMethodRest[modifiers, type]
    |   annotationConstantRest[modifiers, type]
    ;
    
annotationMethodRest[modifiers, type]
@after {retval.tree.is_statement = True; retval.tree.is_method_statement = True;\
        retval.tree.instruction_class = "METHOD_DECLARATION"; retval.tree.instruction = "ANNOTATION_METHOD_DECLARATION";}
    :   identifier '(' ')' (defaultValue)?
        -> ^(ANNOTATION_METHOD {modifiers} {type} identifier defaultValue?)
    ;
    
annotationConstantRest[modifiers, type]
    :   variableDeclarators
        -> ^(FIELD_DECLARATION {$modifiers} {$type} variableDeclarators)
    ;
    
defaultValue
@after {retval.tree.instruction_class = "ANNOTATION_METHOD"; \
        retval.tree.instruction = "ANNOTATION_METHOD_DEFAULT_VALUE"}
    :   'default' elementValue
        -> ^('default' elementValue)
    ;

// STATEMENTS / BLOCKS

block
@after {retval.tree.is_statement = True}
    :   '{' blockStatement* '}'
        -> ^(BLOCK blockStatement*)
    ;
    
blockStatement
    :   localVariableDeclarationStatement
    |   classOrInterfaceDeclaration[None]
    |   statement
    ;
    
localVariableDeclarationStatement
    :    localVariableDeclaration ';'!
    ;

localVariableDeclaration
@after {retval.tree.is_statement = True}
    :   variableModifiers type variableDeclarators
        -> ^(LOCAL_VARIABLE_DECLARATION variableModifiers type variableDeclarators)
    ;
    
variableModifiers
    :   variableModifier*
        -> ^(MODIFIERS variableModifier*)
    ;

statement
@after {retval.tree.is_statement = True}
    : block
    |   ASSERT e1=expression (':' e2=expression)? ';'
        -> ^(ASSERT_STATEMENT $e1 $e2?)
    |   if_statement
    |   for_statement
    |   while_statement
    |   do_while_statement
    |   try_statement
    |   switch_statement
    |   synchronized_statement
    |   return_statement
    |   throw_statement
    |   break_statement
    |   continue_statement
    |   ';' 
        -> EMPTY_STATEMENT
    |   statementExpression ';'
        -> ^(EXPRESSION_STATEMENT statementExpression)
    |   identifier ':' statement
        -> ^(':' identifier statement)
    ;

if_statement
@after {retval.tree.instruction_class = "CONDITIONAL_STATEMENT"; retval.tree.instruction = "IF_STATEMENT"}
    :   'if' parExpression statement (options {k=1;}:'else' statement)?
        -> ^('if' parExpression statement+)
    ;

for_statement
@after {retval.tree.instruction_class = "LOOP_STATEMENT"; retval.tree.instruction = "FOR_STATEMENT"}
    :   'for' '(' forControl ')' statement
        -> ^('for' forControl statement)
    ;

while_statement
@after {retval.tree.instruction_class = "LOOP_STATEMENT"; retval.tree.instruction = "WHILE_STATEMENT"}
    :   'while'^ parExpression statement
        -> ^('while' parExpression statement)
    ;

do_while_statement
@after {retval.tree.instruction_class = "LOOP_STATEMENT"; retval.tree.instruction = "DOWHILE_STATEMENT"}
    :   'do' statement 'while' parExpression ';'
        -> ^('do' statement parExpression)
    ;


try_statement
@after {retval.tree.instruction_class = "CONTROLFLOW_STATEMENT"; retval.tree.instruction = "EXCEPTION_TRY"}
    :   'try' tryBlock=block
        ( catches finallyClause
            -> ^('try' $tryBlock catches finallyClause)
        | catches
            -> ^('try' $tryBlock catches)
        | finallyClause
            -> ^('try' $tryBlock finallyClause)
        )
    ;

catches
    :   catchClause (catchClause)*
    ;
    
catchClause
@after {retval.tree.instruction_class = "CONTROLFLOW_STATEMENT"; retval.tree.instruction = "EXCEPTION_CATCH"}
    :   'catch' '(' formalParameter ')' block
        -> ^('catch' formalParameter block)
    ;

finallyClause
@after {retval.tree.instruction_class = "CONTROLFLOW_STATEMENT"; retval.tree.instruction = "EXCEPTION_FINALLY"}
    :   'finally' finallyBlock=block
        -> ^('finally' $finallyBlock)
    ;

switch_statement
@after {retval.tree.instruction_class = "CONDITIONAL_STATEMENT"; retval.tree.instruction = "SWITCH_STATEMENT"}
    :   'switch' parExpression '{' switchBlockStatementGroups '}'
        -> ^('switch' parExpression switchBlockStatementGroups)
    ;

synchronized_statement
@after {retval.tree.instruction_class = "CONTROLFLOW_STATEMENT"; retval.tree.instruction = "SYNC_THREAD_ACCESS_MODIFIER"}
    :   'synchronized' parExpression block
        -> ^('synchronized' parExpression block)
    ;

return_statement
@after {retval.tree.instruction_class = "CONTROLFLOW_STATEMENT"; retval.tree.instruction = "RETURN_STATEMENT"}
    :   'return' expression? ';'
        -> ^('return' expression?)
    ;

throw_statement
@after {retval.tree.instruction_class = "CONTROLFLOW_STATEMENT"; retval.tree.instruction = "EXCEPTION_THROW"}
    :   'throw' expression ';'
        -> ^('throw' expression)
    ;

break_statement
@after {retval.tree.instruction_class = "CONTROLFLOW_STATEMENT"; retval.tree.instruction = "BREAK_STATEMENT"}
    :   'break' identifier? ';'
        -> ^('break' identifier?)
    ;

continue_statement
@after {retval.tree.instruction_class = "CONTROLFLOW_STATEMENT"; retval.tree.instruction = "CONTINUE_STATEMENT"}
    :   'continue' identifier? ';'
        -> ^('continue' identifier?)
    ;

formalParameter
    :   variableModifiers type variableDeclaratorId
        -> ^(FORMAL_PARAMETER variableModifiers type variableDeclaratorId)
    ;
        
switchBlockStatementGroups
    :   (switchBlockStatementGroup)*
    ;
    
/* The change here (switchLabel -> switchLabel+) technically makes this grammar
   ambiguous; but with appropriately greedy parsing it yields the most
   appropriate AST, one in which each group, except possibly the last one, has
   labels and statements. */
switchBlockStatementGroup
    :   switchLabel+ blockStatement*
        -> ^(SWITCH_BLOCK_STATEMENT_GROUP switchLabel+ blockStatement*)
    ;
    
switchLabel
@after {retval.tree.instruction_class = "CONDITIONAL_STATEMENT"; retval.tree.instruction = "CASE_STATEMENT"}
    :   'case'^ constantExpression ':'!
    |   'case'^ enumConstantName ':'!
    |   'default'^ ':'!
    ;
    
forControl
options {k=3;} // be efficient for common case: for (ID ID : ID) ...
    :   enhancedForControl
    |   forInit? ';' expression? ';' forUpdate?
        -> ^(BASIC_FOR_CONTROL forInit? expression? forUpdate?) //Eliminato ';'
    ;

forInit
    :   localVariableDeclaration
        -> ^(FOR_INIT_DECLARATION localVariableDeclaration)
    |   expressionList
        -> ^(FOR_INIT_EXPRESSION_LIST expressionList)
    ;
    
enhancedForControl
    :   variableModifiers type identifier ':' expression
        -> ^(ENHANCED_FOR_CONTROL variableModifiers type identifier expression)
    ;

forUpdate
    :   expressionList
        -> ^(FOR_UPDATE expressionList)
    ;

// EXPRESSIONS

parExpression
    :   '('! expression ')'!
    ;
    
expressionList
    :   expression (',' expression)*
        -> ^(EXPRESSION_LIST expression+)
    ;

statementExpression
    :   expression
    ;
    
constantExpression
    :   expression
    ;
    
expression
    :   conditionalExpression (assignmentOperator^ expression)?
    ;
    
assignmentOperator
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "ASSIGNEMENT_OPERATOR"}
    :   '='
    |   '+='
    |   '-='
    |   '*='
    |   '/='
    |   '&='
    |   '|='
    |   '^='
    |   '%='
    |   ('<' '<' '=')=> t1='<' t2='<' t3='=' 
        { $t1.getLine() == $t2.getLine() and
          $t1.getCharPositionInLine() + 1 == $t2.getCharPositionInLine() and 
          $t2.getLine() == $t3.getLine() and 
          $t2.getCharPositionInLine() + 1 == $t3.getCharPositionInLine() }?
        -> LEFT_SHIFT_ASSIGN
    |   ('>' '>' '>' '=')=> t1='>' t2='>' t3='>' t4='='
        { $t1.getLine() == $t2.getLine() and 
          $t1.getCharPositionInLine() + 1 == $t2.getCharPositionInLine() and
          $t2.getLine() == $t3.getLine() and 
          $t2.getCharPositionInLine() + 1 == $t3.getCharPositionInLine() and
          $t3.getLine() == $t4.getLine() and 
          $t3.getCharPositionInLine() + 1 == $t4.getCharPositionInLine() }?
        -> UNSIGNED_RIGHT_SHIFT_ASSIGN
    |   ('>' '>' '=')=> t1='>' t2='>' t3='='
        { $t1.getLine() == $t2.getLine() and
          $t1.getCharPositionInLine() + 1 == $t2.getCharPositionInLine() and 
          $t2.getLine() == $t3.getLine() and 
          $t2.getCharPositionInLine() + 1 == $t3.getCharPositionInLine() }?
        -> SIGNED_RIGHT_SHIFT_ASSIGN
    ;

conditionalExpression
    :   conditionalOrExpression ( questmarkOp^ expression ':'! expression )?
    ;

questmarkOp
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "CONDITIONAL_OPERATOR"}
    :   '?'
    ;

conditionalOrExpression
    :   conditionalAndExpression (conditionalOrOp^ conditionalAndExpression )*
    ;

conditionalOrOp
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "CONDITIONAL_OPERATOR"}
    :    '||'
    ;

conditionalAndExpression
    :   inclusiveOrExpression (conditionalAndOp^ inclusiveOrExpression)*
    ;

conditionalAndOp
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "CONDITIONAL_OPERATOR"}
    :   '&&'
    ;

inclusiveOrExpression
    :   exclusiveOrExpression (bitwiseOrOp^ exclusiveOrExpression)*
    ;

bitwiseOrOp
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "BITWISE_OPERATOR"}
    :   '|'
    ;

exclusiveOrExpression
    :   andExpression (bitwiseComplementOp^ andExpression)*
    ;

bitwiseComplementOp
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "BITWISE_OPERATOR"}
    :   '^'
    ;

andExpression
    :   equalityExpression (bitwiseAndOp^ equalityExpression)*
    ;

bitwiseAndOp
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "BITWISE_OPERATOR"}
    :   '&'
    ;

equalityExpression
    :   instanceOfExpression (equalityOp^ instanceOfExpression)*
    ;

equalityOp
@after{retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "EQUALITY_OPERATOR"}
    :   ('==' | '!=')
    ;

instanceOfExpression
    :   relationalExpression (instanceOfOp^ type)?
    ;

instanceOfOp
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "TYPE_COMPARISON_OPERATOR"}
    :   'instanceof'
    ;

relationalExpression
    :   shiftExpression (relationalOp^ shiftExpression)*
    ;
    
relationalOp
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "RELATIONAL_OPERATOR"}
    :   ('<' '=')=> t1='<' t2='=' 
        { $t1.getLine() == $t2.getLine() and 
          $t1.getCharPositionInLine() + 1 == $t2.getCharPositionInLine() }?
        -> LESS_THAN_OR_EQUAL_TO
    |   ('>' '=')=> t1='>' t2='=' 
        { $t1.getLine() == $t2.getLine() and 
          $t1.getCharPositionInLine() + 1 == $t2.getCharPositionInLine() }?
        -> GREATER_THAN_OR_EQUAL_TO
    |   '<' 
    |   '>' 
    ;

shiftExpression
    :   additiveExpression (shiftOp^ additiveExpression)*
    ;

shiftOp
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "SHIFT_OPERATOR"}
    :   ('<' '<')=> t1='<' t2='<' 
        { $t1.getLine() == $t2.getLine() and 
          $t1.getCharPositionInLine() + 1 == $t2.getCharPositionInLine() }?
        -> LEFT_SHIFT
    |   ('>' '>' '>')=> t1='>' t2='>' t3='>' 
        { $t1.getLine() == $t2.getLine() and 
          $t1.getCharPositionInLine() + 1 == $t2.getCharPositionInLine() and
          $t2.getLine() == $t3.getLine() and 
          $t2.getCharPositionInLine() + 1 == $t3.getCharPositionInLine() }?
        -> UNSIGNED_RIGHT_SHIFT
    |   ('>' '>')=> t1='>' t2='>'
        { $t1.getLine() == $t2.getLine() and 
          $t1.getCharPositionInLine() + 1 == $t2.getCharPositionInLine() }?
        -> SIGNED_RIGHT_SHIFT 
    ;


additiveExpression
    :   multiplicativeExpression (additiveOp^ multiplicativeExpression)*
    ;

additiveOp
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "ADDITIVE_OPERATOR"}
    :   '+' 
    |   '-'
    ;

multiplicativeExpression
    :   unaryExpression (multiplicativeOp^ unaryExpression)*
    ;

multiplicativeOp
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "MULTIPLICATIVE_OPERATOR"}
    :   '*' 
    |   '/' 
    |   '%'
    ;

unaryExpression
    :   unaryPlusExpr   
        -> ^(PREFIX_EXPRESSION unaryPlusExpr)
    |   unaryMinusExpr   
        -> ^(PREFIX_EXPRESSION unaryMinusExpr)
    |   unaryDoublePlusExpr
        -> ^(PREFIX_EXPRESSION unaryDoublePlusExpr)
    |   unaryDoubleMinusExpr
        -> ^(PREFIX_EXPRESSION unaryDoubleMinusExpr)
    |   unaryExpressionNotPlusMinus
    ;

unaryExpressionNotPlusMinus
    :   unaryTildeExpr     -> ^(PREFIX_EXPRESSION unaryTildeExpr)
    |   unaryExclaExpr     -> ^(PREFIX_EXPRESSION unaryExclaExpr)
    |   castExpression
    |   ( primary -> primary )
        ( (selector[None])=> selector[$unaryExpressionNotPlusMinus.tree]
            -> selector )*
        (  ( '++' -> ^(POST_INCREMENT_EXPRESSION $unaryExpressionNotPlusMinus )
           | '--' -> ^(POST_DECREMENT_EXPRESSION $unaryExpressionNotPlusMinus )
           ) )?
    ;

unaryPlusExpr
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "ADDITIVE_OPERATOR"}
    :   '+'^ unaryExpression
    ;

unaryMinusExpr
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "ADDITIVE_OPERATOR"}
    :   '-'^ unaryExpression
    ;

unaryDoublePlusExpr
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "ADDITIVE_OPERATOR"}
    :   '++'^ unaryExpression
    ;
    
unaryDoubleMinusExpr
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "ADDITIVE_OPERATOR"}
    :   '--'^ unaryExpression
    ;
    
unaryTildeExpr
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "BITWISE_OPERATOR"}
    :   '~'^ unaryExpression
    ;

unaryExclaExpr
@after {retval.tree.instruction_class = "OPERATOR"; retval.tree.instruction = "LOGICAL_OPERATOR"}
    :   '!'^ unaryExpression
    ;

castExpression
    :  '(' primitiveType ')' unaryExpression
        -> ^(CAST primitiveType unaryExpression)
    |  '(' (type | expression) ')' unaryExpressionNotPlusMinus
        -> ^(CAST type? expression? unaryExpressionNotPlusMinus)
    ;

primary
    :   parExpression
    |   ( 'this' -> THIS)
        ( '.' identifier -> ^(SELECT $primary identifier) )*
        ( (identifierSuffix[None])=> identifierSuffix[$primary.tree] -> identifierSuffix )?
    |   ( 'super' -> UNQUALIFIED_SUPER ) 
        superSuffix[$primary.tree] -> superSuffix
    |   literal
    |   'new' creator
        -> creator
    |   ( identifier -> identifier )
        ( '.' identifier -> ^(SELECT $primary identifier) )*
        ( (identifierSuffix[None])=> identifierSuffix[$primary.tree] -> identifierSuffix )?
    |   ( primitiveType -> primitiveType )
        ( '[' ']' -> ^(ARRAY_OF $primary) )*
        '.' 'class' -> ^(CLASS_DESIGNATOR $primary)
    |   'void' '.' 'class'
        -> ^(CLASS_DESIGNATOR VOID)
    ;

identifierSuffix[expr]
    :   ( '[' ']' -> ^(ARRAY_OF {expr}))
        ( '[' ']' -> ^(ARRAY_OF $identifierSuffix) )*
        ( '.' 'class' -> ^(CLASS_DESIGNATOR $identifierSuffix) )
    |   (-> {expr})
        ('[' expression ']' -> ^(ARRAY_ACCESS $identifierSuffix expression))+
    |   arguments
        -> ^(CALL {expr} arguments)
    |   '.' 'class'
        -> ^(CLASS_DESIGNATOR {expr})
    |   '.' explicitGenericInvocation[expr]
        -> explicitGenericInvocation
    |   '.' 'this'
        -> ^(QUALIFIED_THIS {expr})
    |   '.' 'super' arguments
        -> ^(CALL ^(QUALIFIED_SUPER {expr}) arguments)
    |   '.' 'new' innerCreator[expr]
        -> innerCreator
    ;

creator
    :   nonWildcardTypeArguments createdName classCreatorRest
        -> ^(UNQUALIFIED_CLASS_INSTANCE_CREATION nonWildcardTypeArguments createdName classCreatorRest)
    |   createdName
        (   (arrayCreatorRest[$createdName.tree]
            -> arrayCreatorRest)
        |   classCreatorRest
            -> ^(UNQUALIFIED_CLASS_INSTANCE_CREATION createdName classCreatorRest)
        )
    ;

createdName
    :   classOrInterfaceType
    |   primitiveType
    ;
    
innerCreator[expr]
    :   (nonWildcardTypeArguments)? identifier classCreatorRest
        -> ^(QUALIFIED_CLASS_INSTANCE_CREATION {expr} nonWildcardTypeArguments? identifier classCreatorRest)
    ;

arrayCreatorRest[name]
    :   
        dims arrayInitializer
        -> ^(NEW_INITIALIZED_ARRAY {$name} dims arrayInitializer)
    |   '[' expression ']' ('[' expression ']')* dims?
        -> ^(NEW_ARRAY {$name} expression+ dims?)
    ;

dims
    :   (result+='[' ']')+
        -> $result
    ;

classCreatorRest
    :   arguments classBody?
    ;
    
explicitGenericInvocation[expr]
    :   nonWildcardTypeArguments identifier arguments
        -> ^(EXPLICIT_GENERIC_INVOCATIONS {expr} nonWildcardTypeArguments identifier arguments)
    ;
    
nonWildcardTypeArguments
    :   '<' typeList '>'
        -> ^(NON_WILD_TYPE_ARGUMENTS typeList)
    ;
    
selector[expr]
    :   ('.' identifier -> ^(SELECT {expr} identifier))
        (arguments -> ^(CALL $selector arguments))?
    |   '.' 'this'
        -> ^(INNER_THIS {expr})
    |   ( '.' 'super' -> ^(QUALIFIED_SUPER {expr}) )
        superSuffix[$selector.tree]
        -> superSuffix
    |   '.' 'new' innerCreator[expr]
        -> innerCreator
    |   '[' expression ']'
        -> ^(ARRAY_ACCESS {expr} expression)
    ;
    
superSuffix[expr]
    :   arguments
        -> ^(CALL {expr} arguments)
    |   ('.' identifier -> ^(SELECT {$expr} identifier))
        ( arguments -> ^(CALL $superSuffix arguments))?
    ;

arguments
    :   '(' expressionList? ')'
        -> ^(ARGUMENTS expressionList?)
    ;

identifier
@after {retval.tree.instruction_class = "IDENTIFIER"; retval.tree.instruction = "IDENTIFIER";}
    :   Identifier
    ;

// Modifiers

public_mod
@after {retval.tree.instruction_class = "MODIFIER"; retval.tree.instruction = "ACCESS_LEVEL_MODIFIER"}
    :   'public'
    ;

protected_mod
@after {retval.tree.instruction_class = "MODIFIER"; retval.tree.instruction = "ACCESS_LEVEL_MODIFIER"}
    :   'protected'
    ;
    
private_mod
@after {retval.tree.instruction_class = "MODIFIER"; retval.tree.instruction = "ACCESS_LEVEL_MODIFIER"}
    :   'private'
    ;
    
static_mod
@after {retval.tree.instruction_class = "MODIFIER"; retval.tree.instruction = "ACCESS_LEVEL_MODIFIER"}
    :   'static'
    ;
    
abstract_mod
@after {retval.tree.instruction_class = "MODIFIER"; retval.tree.instruction = "ACCESS_LEVEL_MODIFIER"}
    :   'abstract'
    ;
    
final_mod
@after {retval.tree.instruction_class = "MODIFIER"; retval.tree.instruction = "ACCESS_LEVEL_MODIFIER"}
    :   'final'
    ;

native_mod
@after {retval.tree.instruction_class = "MODIFIER"; retval.tree.instruction = "NATIVE_LANG_MODIFIER"}
    :   'native'
    ;
    
synchronized_mod
@after {retval.tree.instruction_class = "MODIFIER"; retval.tree.instruction = "SYNC_THREAD_ACCESS_MODIFIER"}
    :   'synchronized'
    ;
    
transient_mod
@after {retval.tree.instruction_class = "MODIFIER"; retval.tree.instruction = "PERSISTENCE_MODIFIER"}
    :   'transient'
    ;
    
volatile_mod
@after {retval.tree.instruction_class = "MODIFIER"; retval.tree.instruction = "ASYNC_THREAD_ACCESS_MODIFIER"}
    :   'volatile'
    ;
    
strictfp_mod
@after {retval.tree.instruction_class = "MODIFIER"; retval.tree.instruction = "FLOATING_POINT_MODIFIER"}
    :   'strictfp'
    ;


// LEXER

HexLiteral : '0' ('x'|'X') HexDigit+ IntegerTypeSuffix? ;

DecimalLiteral : ('0' | '1'..'9' '0'..'9'*) IntegerTypeSuffix? ;

OctalLiteral : '0' ('0'..'7')+ IntegerTypeSuffix? ;

fragment
HexDigit : ('0'..'9'|'a'..'f'|'A'..'F') ;

fragment
IntegerTypeSuffix : ('l'|'L') ;

FloatingPointLiteral
    :   ('0'..'9')+ '.' ('0'..'9')* Exponent? FloatTypeSuffix?
    |   '.' ('0'..'9')+ Exponent? FloatTypeSuffix?
    |   ('0'..'9')+ Exponent FloatTypeSuffix?
    |   ('0'..'9')+ FloatTypeSuffix
    ;

fragment
Exponent : ('e'|'E') ('+'|'-')? ('0'..'9')+ ;

fragment
FloatTypeSuffix : ('f'|'F'|'d'|'D') ;

CharacterLiteral
    :   '\'' ( EscapeSequence | ~('\''|'\\') ) '\''
    ;

StringLiteral
    :  '"' ( EscapeSequence | ~('\\'|'"') )* '"'
    ;

fragment
EscapeSequence
    :   '\\' ('b'|'t'|'n'|'f'|'r'|'\"'|'\''|'\\')
    |   UnicodeEscape
    |   OctalEscape
    ;

fragment
OctalEscape
    :   '\\' ('0'..'3') ('0'..'7') ('0'..'7')
    |   '\\' ('0'..'7') ('0'..'7')
    |   '\\' ('0'..'7')
    ;

fragment
UnicodeEscape
    :   '\\' 'u' HexDigit HexDigit HexDigit HexDigit
    ;

ENUM:   'enum' 
        {
            if not(self.enumIsKeyword):
                $type=Identifier;
        }
    ;
    
ASSERT
    :   'assert' 
        {
            if not(self.assertIsKeyword):
                $type=Identifier;
        }
    ;
    
Identifier 
    :   Letter (Letter|JavaIDDigit)*
    ;

/**I found this char range in JavaCC's grammar, but Letter and Digit overlap.
   Still works, but...
 */
fragment
Letter
    :  '\u0024' |
       '\u0041'..'\u005a' |
       '\u005f' |
       '\u0061'..'\u007a' |
       '\u00c0'..'\u00d6' |
       '\u00d8'..'\u00f6' |
       '\u00f8'..'\u00ff' |
       '\u0100'..'\u1fff' |
       '\u3040'..'\u318f' |
       '\u3300'..'\u337f' |
       '\u3400'..'\u3d2d' |
       '\u4e00'..'\u9fff' |
       '\uf900'..'\ufaff'
    ;

fragment
JavaIDDigit
    :  '\u0030'..'\u0039' |
       '\u0660'..'\u0669' |
       '\u06f0'..'\u06f9' |
       '\u0966'..'\u096f' |
       '\u09e6'..'\u09ef' |
       '\u0a66'..'\u0a6f' |
       '\u0ae6'..'\u0aef' |
       '\u0b66'..'\u0b6f' |
       '\u0be7'..'\u0bef' |
       '\u0c66'..'\u0c6f' |
       '\u0ce6'..'\u0cef' |
       '\u0d66'..'\u0d6f' |
       '\u0e50'..'\u0e59' |
       '\u0ed0'..'\u0ed9' |
       '\u1040'..'\u1049'
   ;

WS  :  (' '|'\r'|'\t'|'\u000C'|'\n') {$channel=HIDDEN;}
    ;

COMMENT
    :   '/*' (options {greedy=false;} : .)* '*/' {$channel=HIDDEN;}
    ;

LINE_COMMENT
    : '//' ~('\n'|'\r')* '\r'? '\n' {$channel=HIDDEN;}
    ;
