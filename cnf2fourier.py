#!/usr/bin/python3

import argparse
import sympy
import math

class Literal:
    def __init__(self, variable_name, is_negated):
        self._variable_name = variable_name
        self._is_negated = is_negated

    def variable_name(self):
        return self._variable_name

    def is_negated(self):
        return self._is_negated
        
    def evaluate(self, variable_value):
        if self._is_negated:
            return not variable_value
        else:
            return variable_value
        
class Clause:
    def __init__(self):
        self._literals = []
    
    def push_back(self, literal):
        self._literals.append(literal)

    def literals(self):
        return self._literals
    
    def num_literals(self):
        return len(self._literals)
    
    # variables is a list of bool
    def evaluate_by_index(self, variables):
        result = False
        for lit in self._literals:
            result |= lit.evaluate(variables[lit.variable_index()])
        return result
        
    def evaluate_by_name(self, variables):
        result = False
        for lit in self._literals:
            if lit.variable_name() in variables:
                result |= lit.evaluate(variables[lit.variable_name()])
        return result
    
    
class Cnf:
    def __init__(self):
        self.clear()
        
    def push_back(self, clause):
        # update the variable name index
        for lit in clause.literals():
            if lit.variable_name() not in self._variable_name_to_index:
                self._variable_name_to_index[lit.variable_name()] = len(self._variable_name_to_index)
        self._clauses.append(clause)
        
    def clear(self):
        self._clauses = []
        self._variable_name_to_index = dict()
        

    def lookup_index(self, name):
        if name in self._variable_name_to_index:
            return self._variable_name_to_index[name]
        else:
            raise Exception("variable name lookup failed")
            
    def variable_name_to_index(self):
        return self._variable_name_to_index;
        
    def num_clauses(self):
        return len(self._clauses)
    
    def clauses(self):
        return self._clauses
    
    def num_variables(self):
        return len(self._variable_name_to_index)
    
class Interval_Value_1:
    def __init__ (self, period, offset, count) :
        self._period = period
        self._offset = offset
        self._count = count

    def period(self):
        return self._period
    
    def offset(self):
        return self._offset
    
    def count(self):
        return self._count
    


class Fourier_Series_Formula:
    def __init__(self, cnf, max_n, use_symbols=True):
        self._cnf = cnf
        self._max_n = max_n
        self._intervals = []
        self._formula = None
        
        for clause in self._cnf.clauses():
            intervals = []
            for lit in clause.literals():
                index = self._cnf.lookup_index(lit.variable_name())
                period = 2 ** (index + 1)
                count = 2 ** index
                offset = count if lit.is_negated() else 0
                intervals.append(Interval_Value_1(period, offset, count))
            self._intervals.append(intervals);    
        
        self.generate_formula(use_symbols)

    def formula(self):
        return self._formula
    
    def coef_integral(self, n, interval, use_symbols=False, symbol_index=0):
        
        if use_symbols:
            iv_period_str = "cp_" + str(symbol_index)
            iv_from_str = "cf_" + str(symbol_index)
            iv_to_str = "ct_" + str(symbol_index)
            (iv_period, iv_from, iv_to) = sympy.symbols(' '.join([iv_period_str,iv_from_str,iv_to_str]))
        else:    
            iv_period = sympy.sympify(interval.period())
            iv_from = sympy.sympify(interval.offset())
            iv_to = sympy.sympify(interval.offset() + interval.count())
        
        coef = 0
        if n == 0:
            coef = iv_to - iv_from
        else:
            fact = -2 * sympy.I * sympy.pi * n / iv_period 
            
            to_fact = sympy.exp(iv_to * fact)
            from_fact = sympy.exp(iv_from * fact)
            
            num = sympy.I * (iv_period / (2*n))
            tmp = num / sympy.pi
            coef = tmp * ( to_fact - from_fact )
        
        coef = coef  / iv_period
        #print("n = ", n)
        
        #print ("coef for n is :{0} {1} ".format(n,coef))
        return coef
            
    
    def get_fourier_series(self, interval, use_symbols=True, symbol_index=0):
        #expr, coef, tmp, sum = integer(0);

        x = sympy.symbols('x')
        s = None
        if use_symbols:
            iv_period_str = "cp_" + str(symbol_index)
            iv_period = sympy.symbols(iv_period_str)
        else:
            iv_period = interval.period()
        
        for n in range(-1 * self._max_n, self._max_n+1):
            
            coef = self.coef_integral(n, interval, use_symbols, symbol_index)
            if n == 0:
                expr = coef
            else:
                tmp = sympy.I * 2 * sympy.pi * n * x / iv_period                
                expr = coef * sympy.exp(tmp)
            if s is None:
                s = expr
            else:
                s = s + expr
            #print(s)
            
        return s
            
        
    def generate_formula(self, use_symbols=True):
        self._formula = None
        symbol_index = 0
        
        for interval in self._intervals:
            lit_mult = None
            for lit_interval in interval:
                fs = self.get_fourier_series(lit_interval, use_symbols, symbol_index)
                symbol_index += 1
                if lit_mult is None:
                    lit_mult = fs
                else:
                    lit_mult = lit_mult * fs
                
            s = 1 - lit_mult
            if self._formula is None:
                self._formula = s
            else:
                self._formula = self._formula * s
            
            
parser = argparse.ArgumentParser(
                    prog='cnf2fourier',
                    description='Creates a mathematical formula from a cnf dimacs file',
                    epilog='-----')

parser.add_argument(
    '-n', '--max_n', required=True, 
    help="Fourier series summation -1*max_n to max_n value"
    ) 
parser.add_argument(
    '-i', '--input', required=True, 
    help="<filename (input)>: DIMACS filename"
    )
parser.add_argument(
    '-o', '--output', required=True, 
    help="<filename (output)>: "
    )
parser.add_argument(
    '-s', '--solve', action='store_true', 
    required=False, 
    help="Try to solve using the symbolic intergration method and searching for a solution"
    )


args = parser.parse_args()
cnf = Cnf()

with open(args.input) as input_file:
    for line in input_file:
        tokens = line.split()
        
        if len(tokens) != 0 and tokens[0] not in ("p", "c"):
            curr_clause = Clause()
            for tok in tokens:
                tok = int(tok)
                if tok == 0:
                    if curr_clause.num_literals() != 3:
                        raise Exception("This program only supports 3-CNF")
                    break
           
                name = abs(tok)
                           
                lit = Literal(name, tok < 0)
                
                curr_clause.push_back(lit);
  
            cnf.push_back(curr_clause)
        

print("Creating forumula...")
fm = Fourier_Series_Formula(cnf, int(args.max_n), False)
with open (args.output, "w") as output_file:    
    output_file.write(str(fm.formula()) + "\n")
    output_file.close()


if (args.solve):
    print("Processing integral...")
    x = sympy.symbols('x')
    F = sympy.integrate(fm.formula(), x) 
    (a,b) = (0, 2 ** cnf.num_variables())
    print("searching for solutions between {0} {1}".format(a,b))
    
    def num_solutions(a, b):
        solutions =  float(sympy.re(sympy.N(F.subs(x, b) - F.subs(x, a))))
        print("Number of solutions between {0} {1}: {2}" .format(a, b, solutions))
        return solutions
    
    solution_found = False
    while True:
        a_0 = a
        b_0 = a + (b-a)/2
        a_1 = b_0
        b_1 = b
        solution_count_0 = num_solutions(a_0, b_0)
        solution_count_1 = num_solutions(a_1, b_1) 
        
        if solution_count_1 > solution_count_0:
            a = a_1
            b = b_1
            solution_found = (solution_count_1 > .8)
        else:
            a = a_0
            b = b_0
            solution_found = (solution_count_1 > .8)
        if (b-a <= 1):
            break
        


    if solution_found:
        print("Solution found. Variable assignments: ") 
        a = int(math.floor(a))    
        for var in cnf.variable_name_to_index().keys():
            index = cnf.lookup_index(var)
            value = 1 if a & (1<<index) != 0 else 0
            print ("{0}: {1}".format(var, value))
    else:
        print ("No solution found")
        





