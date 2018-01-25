import random

bin_dict = {
    '0000': '0',
    '0001': '1',
    '0010': '2',
    '0011': '3',
    '0100': '4',
    '0101': '5',
    '0110': '6',
    '0111': '7',
    '1000': '8',
    '1001': '9',
    '1010': '+',
    '1011': '-',
    '1100': '*',
    '1101': '/'
}


def assign_fitness(tar, c):
    """
    Finds the fitness of the equation
    Divides one by the absolute value of the difference of the target and n
    c is the chromosome binary
    If divide by zero, a solution has been found
    """
    def make_equation(s):
        """
        Reads the combination of bits and creates the output
        Ignores bits above 1101 and those not in order num -> op -> num etc
        ex: 000110100101 -> 1 + 5
        """
        def toggle_bool(b):
            """Changes a boolean between true and false"""
            return False if b else True

        def rmv_ending_operators(eq):
            """Removes ending operators from the string"""
            count = 0
            for n in range(len(eq)):
                if count == len(eq):
                    return eq
                elif eq[-n - 1] in ['+', '-', '*', '/']:
                    count += 1
                else: return eq[:-count] if count > 0 else eq

        was_num = False
        equation = ''
        try:
            for i in range(len(s) // 4):
                bits = s[i * 4:(i + 1) * 4]  # selects four bits to analyze
                if not was_num and bits < '1010' or was_num and '1101' >= bits >= '1010':
                    equation += bin_dict[bits]
                    was_num = toggle_bool(was_num)
        except TypeError as e:
            print(e)
            print(s)
        try:
            if equation == '':
                return -999
            eq = rmv_ending_operators(equation)
            return eval(eq) if eq != '' else -1
        except ZeroDivisionError:
            return -1

    eq_ans = make_equation(c)

    return c, 'Done' if eq_ans == tar else 1 / (tar - eq_ans)


def roulette(lst):
    """
    Chooses two members from the list to 'mate' by spinning a roulette wheel
    Higher fitness = higher chance to be chosen
    """
    sum_fitness = 0
    for member in lst:
        sum_fitness += member[1]  # member is a tuple returned from assign_fitness that contains (chromo, fitness)

    def select_winner():
        r = random.uniform(0, sum_fitness)
        total = 0
        while total < r:
            for member in lst:
                total += member[1]
                if total >= r:
                    return member[0]

    return select_winner(), select_winner()  # These are the two proud new parents of the next generation


def crossover(chromo1, chromo2, rate):
    """Switches the bits after a random number by a rate% chance"""
    def swap_bits(chromo1, chromo2):
        """Swaps the bits in two chromosomes"""
        if len(chromo1) >= len(chromo2):
            r = random.randint(0, len(chromo2) - 2)
        else:
            r = random.randint(0, len(chromo1) - 2)
        return chromo1[-r:] + chromo2[r:], chromo2[-r:] + chromo1[r:]  # probably doesnt work
    if random.uniform(0, 1) <= rate:
        return chromo1, chromo2
    return swap_bits(chromo1, chromo2)


def mutate(chromo, rate):
    """Swaps a random bit in a chromosome with a rate% chance (low)"""
    c = ''
    for char in chromo:
        if random.uniform(0, 1) <= rate:
            c += '0' if char == '1' else '1'
        else:
            c += char
    return c


def rand_bits():
    """Makes random strings of 20 - 36 bits for testing"""
    def one_byte():
        """Makes one random byte"""
        return str(random.randint(0, 1)) + str(random.randint(0, 1)) + str(random.randint(0, 1)) + str(random.randint(0, 1))

    chromosome = ''
    for _ in range(random.randint(4, 8)):  # makes chromosome have anywhere from 16 to 32 chromosomes
        chromosome += one_byte()

    return chromosome


def gen_test_list(ln):
    """Generates a list with ln chromosomes"""
    test = []
    for _ in range(ln):
        test.append(rand_bits())
    return test


def display_eq(chromo):
    """Takes in a chromosome and prints the equation out"""

    def toggle_bool(b):
        """Changes a boolean between true and false"""
        return False if b else True

    def rmv_ending_operators(eq):
        """Removes ending operators from the string"""
        count = 0
        for n in range(len(eq)):
            if count == len(eq):
                return eq
            elif eq[-n - 1] in ['+', '-', '*', '/']:
                count += 1
            else:
                return eq[:-count] if count > 0 else eq

    was_num = False
    equation = ''
    for i in range(len(chromo) // 4):
        bits = chromo[i * 4:(i + 1) * 4]  # selects four bits to analyze
        if not was_num and bits < '1010' or was_num and '1101' >= bits >= '1010':
            equation += bin_dict[bits]
            was_num = toggle_bool(was_num)
    return rmv_ending_operators(equation)

generation = []  # beginning generation list

test_num = 2**45 - 1  # number you want to add to
start_gen_size = 500
max_gen_size = 500
crossover_rate = 0.7
mutate_rate = 0.001

for chromo in gen_test_list(start_gen_size):  # generates starting test list
    generation.append(assign_fitness(test_num, chromo))

gen_count = 0

while True:  # graph progress of avg fitness?
    new_gen = []
    avg_fit = 0

    print('Generation #', gen_count)
    for chromo in generation:
        if isinstance(chromo[1], str):
            print(chromo)
            print(display_eq(chromo[0]))
            quit(0)
        else:
            avg_fit += chromo[1]
    print('Avg fitness: ', avg_fit / len(generation))
    print(eval(display_eq(generation[0][0])))

    for _ in range(1 + len(generation) // 2):
        parents = roulette(generation)  # selects two new parents each pass
        new_gen.append(mutate(crossover(parents[0], parents[1], crossover_rate)[0], mutate_rate))
        new_gen.append(mutate(crossover(parents[0], parents[1], crossover_rate)[1], mutate_rate))

    gen_count += 1
    generation = []
    for chromo in new_gen[:max_gen_size]:
        generation.append(assign_fitness(test_num, chromo))
