from collections import defaultdict

epsilon = 'ε'
star, union, concat = '*', '+', '.' # 정규 표현식 operator
left_bracket, right_bracket = '(', ')'

# 해당 문자의 유니코드 정수 반환
terminal = [chr(i) for i in range(ord('A'), ord('Z') + 1)] + \
    [chr(i) for i in range(ord('a'), ord('z') + 1)] + \
    [chr(i) for i in range(ord('0'), ord('9') + 1)]

# Construct Finite Automata
class FA:
    # Finite Automata 초기화
    def __init__(self, symbol=set([])):
        self.state_set = set()
        self.symbol = symbol
        self.transitions = defaultdict(defaultdict) # key error를 방지하기 위해 defaultdict 사용
        self.startstate = None
        self.finalstate_set = []

    # 시작 상태 설정
    def set_start(self, state):
        self.startstate = state
        self.state_set.add(state)

    # 종결 상태 추가
    def add_final_state(self, state):
        if isinstance(state, int):
            state = [state]
        for s in state:
            if s not in self.finalstate_set:    # final state set은 집합이므로 중복을 제거
                self.finalstate_set.append(s)

    # 상태 전이 추가
    def add_transition(self, from_state, to_state, input_symbol):
        if isinstance(input_symbol, str):
            input_symbol = set([input_symbol])
        self.state_set.add(from_state)
        self.state_set.add(to_state)
        if from_state in self.transitions and to_state in self.transitions[from_state]:
            self.transitions[from_state][to_state] = self.transitions[from_state][to_state].union(input_symbol)
        else:
            self.transitions[from_state][to_state] = input_symbol

    def add_transition_dict(self, transitions):
        for from_state, to_state_set in transitions.items():
            for state in to_state_set:
                self.add_transition(from_state, state, to_state_set[state])

    # 새로운 FA를 구성
    def new_build(self, startnum):
        translations = {}
        for i in self.state_set:
            translations[i] = startnum
            startnum += 1
        rebuild = FA(self.symbol)
        rebuild.set_start(translations[self.startstate])
        rebuild.add_final_state(translations[self.finalstate_set[0]])
        for from_state, to_state_set in self.transitions.items():
            for state in to_state_set:
                rebuild.add_transition(translations[from_state], translations[state], to_state_set[state])
        return [rebuild, startnum]

    # reduced DFA를 구성하기 위해 equivalent class를 하나의 state로 병합
    def merge(self, equivalent, pos):
        rebuild = FA(self.symbol)
        for from_state, to_state_set in self.transitions.items():
            for state in to_state_set:
                rebuild.add_transition(pos[from_state], pos[state], to_state_set[state])
        rebuild.set_start(pos[self.startstate])
        for s in self.finalstate_set:
            rebuild.add_final_state(pos[s])
        return rebuild

    # epsilon NFA to DFA를 구성하기 위해 epsilon closure를 계산
    def get_epsilon_closure(self, findstate):
        all_state_set = set()
        state_set = [findstate]
        while len(state_set):
            state = state_set.pop()
            all_state_set.add(state)
            if state in self.transitions:
                for tos in self.transitions[state]:
                    if epsilon in self.transitions[state][tos] and tos not in all_state_set:
                        state_set.append(tos)
        return all_state_set

    # move를 통해 상태 전이
    def get_move(self, state, skey):
        if isinstance(state, int):
            state = [state]
        trstate_set = set()
        for st in state:
            if st in self.transitions:
                for tns in self.transitions[st]:
                    if skey in self.transitions[st][tns]:
                        trstate_set.add(tns)
        return trstate_set


# RE를 ε-NFA로 변환하는 클래스
class Re2NFA:
    # 초기화
    def __init__(self, regex):
        self.regex = regex
        self.construct_nfa()

    # 연산자의 우선순위를 설정, * > . > +
    def getPriority(op):
        if op == union:
            return 1
        elif op == concat:
            return 2
        elif op == star:
            return 3
        else:
            return 0

    # 단일 심볼을 표현
    def basic_struct(input_symbol):
        state1 = 0
        state2 = 1
        basic = FA(set([input_symbol]))
        basic.set_start(state1)
        basic.add_final_state(state2)
        basic.add_transition(state1, state2, input_symbol)
        return basic

    # N1 + N2
    def construct_nfa_for_union(N1, N2):
        [N1, m1] = N1.new_build(1)
        [N2, m2] = N2.new_build(m1)
        state1 = 0
        state2 = m2
        union_fa = FA(N1.symbol.union(N2.symbol))
        # 상태 노드 2개 추가: 시작, 종결 / ε-전이 간선 4개, 심볼 전이 간선 2개 추가
        union_fa.set_start(state1)
        union_fa.add_final_state(state2)
        union_fa.add_transition(union_fa.startstate, N1.startstate, epsilon)
        union_fa.add_transition(union_fa.startstate, N2.startstate, epsilon)
        union_fa.add_transition(N1.finalstate_set[0], union_fa.finalstate_set[0], epsilon)
        union_fa.add_transition(N2.finalstate_set[0], union_fa.finalstate_set[0], epsilon)
        union_fa.add_transition_dict(N1.transitions)
        union_fa.add_transition_dict(N2.transitions)
        return union_fa
    
    # N1.N2
    def construct_nfa_for_concat(N1, N2):
        [N1, m1] = N1.new_build(0)
        [N2, m2] = N2.new_build(m1)
        state1 = 0
        state2 = m2 - 1
        concat_fa = FA(N1.symbol.union(N2.symbol))
        # ε-전이 간선 1개 추가
        concat_fa.set_start(state1)
        concat_fa.add_final_state(state2)
        concat_fa.add_transition(N1.finalstate_set[0], N2.startstate, epsilon)
        concat_fa.add_transition_dict(N1.transitions)
        concat_fa.add_transition_dict(N2.transitions)
        return concat_fa

    # N*
    def construct_nfa_for_star(N):
        [N, m1] = N.new_build(1)
        state1 = 0
        state2 = m1
        star_fa = FA(N.symbol)
        # 상태 노드 4개 추가: (시작, 종결) pair 2개 / ε-전이 간선 4개 추가
        star_fa.set_start(state1)
        star_fa.add_final_state(state2)
        star_fa.add_transition(star_fa.startstate, N.startstate, epsilon)
        star_fa.add_transition(star_fa.startstate, star_fa.finalstate_set[0], epsilon)
        star_fa.add_transition(N.finalstate_set[0], star_fa.finalstate_set[0], epsilon)
        star_fa.add_transition(N.finalstate_set[0], N.startstate, epsilon)
        star_fa.add_transition_dict(N.transitions)
        return star_fa

    # construct 함수를 기반으로 nfa를 형성
    def construct_nfa(self):
        word = ''
        pre = ''
        symbol = set()

        for ch in self.regex:
            if ch in terminal:
                symbol.add(ch)
            if ch in terminal or ch == left_bracket:
                if pre != concat and (pre in terminal or pre in [star, right_bracket]):
                    word += concat
            word += ch
            pre = ch
        self.regex = word

        word = ''
        stack = []
        for ch in self.regex:
            if ch in terminal:
                word += ch
            elif ch == left_bracket:
                stack.append(ch)
            elif ch == right_bracket:
                while stack[-1] != left_bracket:
                    word += stack[-1]
                    stack.pop()
                stack.pop()
            else:
                while len(stack) and Re2NFA.getPriority(stack[-1]) >= Re2NFA.getPriority(ch):
                    word += stack[-1]
                    stack.pop()
                stack.append(ch)
        while len(stack) > 0:
            word += stack.pop()
        self.regex = word

        self.automata = []
        for ch in self.regex:
            if ch in terminal:
                self.automata.append(Re2NFA.basic_struct(ch))
            elif ch == union:
                b = self.automata.pop()
                a = self.automata.pop()
                self.automata.append(Re2NFA.construct_nfa_for_union(a, b))
            elif ch == concat:
                b = self.automata.pop()
                a = self.automata.pop()
                self.automata.append(Re2NFA.construct_nfa_for_concat(a, b))
            elif ch == star:
                a = self.automata.pop()
                self.automata.append(Re2NFA.construct_nfa_for_star(a))
        self.nfa = self.automata.pop()
        self.nfa.symbol = symbol
        
    # ε-NFA를 출력형식에 맞게 출력
    def print_nfa(self):
        new_state_set = set()
        state_set = self.nfa.state_set
        terminals = self.nfa.symbol
        transitions = self.nfa.transitions
        start_state = self.nfa.startstate
        final_state_set = self.nfa.finalstate_set
        print("---------ε-NFA---------")
        # state를 새롭게 수정한 뒤 출력
        for state in state_set.copy():
            new_state = f"q{state:03}"
            new_state_set.add(new_state)
        new_state_set = sorted(new_state_set)
        print(f"StateSet = {new_state_set}")
        print(f"TerminalSet = {terminals}")

        print("DeltaFunctions = {")
        for from_state, to_state_set in transitions.items():
            for input_ch, to_state in to_state_set.items():
                print(f"\t({from_state}, {input_ch}) = {to_state}")
        print("}")
        
        start_state = f"q{start_state:03}"
        print(f"StartState = {start_state}")
        
        # final_state를 새롭게 수정한 뒤 출력
        new_final_state_set = []
        for state in final_state_set.copy():
            new_final_state = f"q{state:03}"
            new_final_state_set.append(new_final_state)
        print("FinalstateSet = { ", end = '')
        for i in new_final_state_set:
            print(i, end = ' ')
        print("}")


# ε-NFA를 DFA 및 reduced DFA로 변환하는 클래스
class NFA2DFA:
    def __init__(self, nfa):
        self.construct_dfa(nfa)

    # DFA를 형성
    def construct_dfa(self, nfa):
        all_state_set = dict()  # visited subset
        eclosure = dict()   # 상태들의 ε-closure
        state1 = nfa.get_epsilon_closure(nfa.startstate)
        eclosure[nfa.startstate] = state1
        cnt = 0     # DFA의 상태 id
        dfa = FA(nfa.symbol)
        dfa.set_start(cnt)
        state_set = [[state1, dfa.startstate]]  # unvisit
        all_state_set[cnt] = state1
        cnt += 1
        while len(state_set):
            [state, fromindex] = state_set.pop()
            for ch in dfa.symbol:
                trstate_set = nfa.get_move(state, ch)
                for s in list(trstate_set):
                    if s not in eclosure:
                        eclosure[s] = nfa.get_epsilon_closure(s)
                    trstate_set = trstate_set.union(eclosure[s])
                if len(trstate_set):
                    if trstate_set not in all_state_set.values():
                        state_set.append([trstate_set, cnt])
                        all_state_set[cnt] = trstate_set
                        toindex = cnt
                        cnt += 1
                    else:
                        toindex = [k for k, v in all_state_set.items() if v  ==  trstate_set][0]
                    dfa.add_transition(fromindex, toindex, ch)
            for value, state in all_state_set.items():
                if nfa.finalstate_set[0] in state:
                    dfa.add_final_state(value)
            self.dfa = dfa

    # 기존의 상태 집합(epsilon NFA to DFA)이나 
    # 동등 클래스 상태 집합(DFA to reduced DFA)에 대해 새로운 상태를 부여, 0부터 재카운트
    def renumber_state(state_set, pos):
        cnt = 0
        change = dict()
        for st in state_set:
            if pos[st] not in change:
                change[pos[st]] = cnt
                cnt += 1
            pos[st] = change[pos[st]]

    # DFA to reduced DFA를 위해 상태 수 최소화
    def minimize(self):
        state_set = list(self.dfa.state_set)
        to_state = dict(set())

        for st in state_set:
            for sy in self.dfa.symbol:
                if st in to_state:
                    if sy in to_state[st]:
                        to_state[st][sy] = to_state[st][sy].union(self.dfa.get_move(st, sy))
                    else:
                        to_state[st][sy] = self.dfa.get_move(st, sy)
                else:
                    to_state[st] = {sy : self.dfa.get_move(st, sy)}
                if len(to_state[st][sy]):
                    to_state[st][sy] = to_state[st][sy].pop()
                else:
                    to_state[st][sy] = 0

        equal = dict()  
        pos = dict()

        # initialization 2 sets, nonterminal state_set and final state_set
        equal = {1: set(), 2: set()}
        for st in state_set:
            if st not in self.dfa.finalstate_set:
                equal[1] = equal[1].union(set([st]))
                pos[st] = 1
        for fst in self.dfa.finalstate_set:
            equal[2] = equal[2].union(set([fst]))
            pos[fst] = 2

        unchecked = []
        cnt = 3 # the number of sets
        unchecked.extend([[equal[1], 1], [equal[2], 2]])
        while len(unchecked):
            [equalst, id] = unchecked.pop()
            for sy in self.dfa.symbol:
                diff = dict()
                for st in equalst:
                    if to_state[st][sy] == 0:
                        if 0 in diff:
                            diff[0].add(st)
                        else:
                            diff[0] = set([st])
                    else:
                        if pos[to_state[st][sy]] in diff:
                            diff[pos[to_state[st][sy]]].add(st)
                        else:
                            diff[pos[to_state[st][sy]]] = set([st])
                if len(diff) > 1:
                    for k, v in diff.items():
                        if k:
                            for i in v:
                                equal[id].remove(i)
                                if cnt in equal:
                                    equal[cnt] = equal[cnt].union(set([i]))
                                else:
                                    equal[cnt] = set([i])
                            if len(equal[id]) == 0:
                                equal.pop(id)
                            for i in v:
                                pos[i] = cnt
                            unchecked.append([equal[cnt], cnt])
                            cnt += 1
                    break
        if len(equal) == len(state_set):
            self.min_dfa = self.dfa
        else:
            NFA2DFA.renumber_state(state_set, pos)
            self.min_dfa = self.dfa.merge(equal, pos)

    # DFA를 출력형식에 맞게 출력
    def print_dfa(self):
        new_state_set = set()
        print()
        print("---------DFA---------")
        for state in self.dfa.state_set.copy():  # state를 새롭게 수정한 뒤 출력
            new_state = f"Q{state:03}"
            new_state_set.add(new_state)
        new_state_set = sorted(new_state_set)
        print(f"state_set = {new_state_set}")
        
        print("TerminalSet =", self.dfa.symbol)
        
        print("DeltaFunctions = {")
        for from_state, transitions in self.dfa.transitions.items():
            for symbol, to_state_set in transitions.items():
                print(f"\t({from_state}, {symbol}) = {to_state_set}")
        print("}")
        
        start_state = f"Q{self.dfa.startstate:03}"
        print("StartState =", start_state)
        
        dfa_new_final_state_set = []
        for state in self.dfa.finalstate_set.copy():
            new_final_state = f"Q{state:03}"
            dfa_new_final_state_set.append(new_final_state)
        print("FinalstateSet = { ", end = '')
        for i in dfa_new_final_state_set:
            print(i, end = ' ')
        print("}")
        

    # reduced DFA를 출력형식에 맞게 출력
    def print_reduced_dfa(self):
        new_state_set = set()
        print()
        print("---------reduced DFA---------")
        for state in self.min_dfa.state_set.copy():  # state를 새롭게 수정한 뒤 출력
            new_state = f"M{state:03}"
            new_state_set.add(new_state)
        new_state_set = sorted(new_state_set)
        print("state_set =", new_state_set)
        
        print("TerminalSet =", self.min_dfa.symbol)
        
        print("DeltaFunctions = {")
        for from_state, transitions in self.min_dfa.transitions.items():
            for symbol, to_state_set in transitions.items():
                print(f"\t({from_state}, {symbol}) = {to_state_set}")
        print("}")
        
        start_state = f"M{self.min_dfa.startstate:03}"
        print("StartState =", start_state)
        
        min_new_final_state_set = []
        for state in self.min_dfa.finalstate_set.copy():
            new_final_state = f"M{state:03}"
            min_new_final_state_set.append(new_final_state)
        print("FinalstateSet = { ", end = '')
        for i in min_new_final_state_set:
            print(i, end = ' ')
        print("}")


if __name__ == '__main__':    
    while True:
        re = input('정규 표현식 입력(q만 입력시 종료): ')
        if re != 'q':
            # 정규 표현식을 입력으로 받아 ε-NFA를 구성하고 출력
            regex2nfa = Re2NFA(re)
            regex2nfa.print_nfa()

            # DFA를 구성하고 출력
            fa = NFA2DFA(regex2nfa.nfa)
            fa.print_dfa()

            # reduced DFA를 구성하고 출력
            fa.minimize()
            fa.print_reduced_dfa()
        else:
            break
