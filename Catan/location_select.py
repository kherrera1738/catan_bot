priority_resources = {
    0:(0.5,0.3,0.2), 
    1:(0.4,0.3,0.3), 
    2:(0.4,0.3,0.3), 
    3:(0.3,0.35,0.35), 
    4:(0.3,0.3,0.4), 
    5:(0.2,0.3,0.5), 
    6:(0.1,0.2,0.7), 
    7:(0.1,0.3,0.6),
    8:(0.1,0.4,0.5), 
    9:(0.2,0.4,0.4)
}
probs = {
    0 : 0,
    2 : 1/36,
    3 : 2/36,
    4 : 3/36,
    5 : 4/36,
    6 : 5/36,
    7 : 6/36,
    8 : 5/36,
    9 : 4/36,
    10 : 3/36,
    11 : 2/36,
    12 : 1/36
}

def average_city_returns(self, board_dice):
    """Take in dice object and calculates the expected returns of a building over all settlement locations"""
    
    def prob_map(x):
        probs = {
            0 : 0,
            2 : 1/36,
            3 : 2/36,
            4 : 3/36,
            5 : 4/36,
            6 : 5/36,
            7 : 6/36,
            8 : 5/36,
            9 : 4/36,
            10 : 3/36,
            11 : 2/36,
            12 : 1/36
        }
        return probs[x]
    
    values = board_dice
    prob_map = np.vectorize(prob_map)
    values = prob_map(values)
    values = np.pad(values, [(1, 1), (1, 1)], mode='constant')
    vecs = np.zeros(((values.shape[0]-1)*(values.shape[1]-1), 4))
    for i in range(values.shape[0]-1):
        for j in range(values.shape[1]-1):
            vecs[i*(values.shape[1]-1)+ j] = values[i:i+2, j:j+2].reshape(1, 4)
    sum_vec = np.ones(4)
    vecs = np.dot(vecs, sum_vec)
    return np.sum(vecs)/vecs.shape[0]

def handle_port(self, x, y):
    port_const = 1.5
    val = 0
    if(x == 0):
        val = probs[self.board.dice[0, 0]] if y == 0 else probs[self.board.dice[x, y-1]]
    if(x == self.board.height):
        val = probs[self.board.dice[x-1, 0]] if y == 0 else probs[self.board.dice[x-1, y-1]]

    return val * port_const * self.average_city_return(self.board.dice)


def handle_edge(self, x, y):
    loc_val = np.array([0, 0, 0])
    if(x == 0):
        if(self.board.resources[x, y] != -1):
            loc_val[self.board.resources[x, y]] += probs[solf.board.dice[x, y]]
        if(self.board.resources[x, y-1] != -1):
            loc_val[self.board.resources[x, y-1]] += probs[solf.board.dice[x, y-1]]
    elif(x == self.board.height):
        if(self.board.resources[x-1, y] != -1):
            loc_val[self.board.resources[x-1, y]] += probs[solf.board.dice[x-1, y]]
        if(self.board.resources[x-1, y-1] != -1):
            loc_val[self.board.resources[x-1, y-1]] += probs[solf.board.dice[x-1, y-1]]
    elif(y == self.board.width):
        if(self.board.resources[x, y-1] != -1):
            loc_val[self.board.resources[x, y-1]] += probs[solf.board.dice[x, y-1]]
        if(self.board.resources[x-1, y-1] != -1):
            loc_val[self.board.resources[x-1, y-1]] += probs[solf.board.dice[x-1, y-1]]
    else:
        if(self.board.resources[x, y] != -1):
            loc_val[self.board.resources[x, y]] += probs[solf.board.dice[x, y]]
        if(self.board.resources[x-1, y] != -1):
            loc_val[self.board.resources[x-1, y]] += probs[solf.board.dice[x-1, y]]
    return loc_val

def best_loc(self, locations):
    expected = dict()
    score_dist = priority_resources[self.points]
    for loc in locations:
        loc_val = np.array([0, 0, 0])
        x = loc[0]
        y = loc[1]
        if self.board.is_port(loc):
            expected[loc] = handle_port(x, y)
        elif (x == 0 or y == 0 or x == self.board.height or y == self.board.height):
            expected[loc] = np.dot(handle_edge(x, y), score_dist)
        else:
            for i in range(2):
                for j in range(2):
                    if(self.board.resources[x-i, y-j] != -1):
                        loc_val[self.board.resources[x-i, y-j]] += probs[solf.board.dice[x-i, y-j]] 
            expected[loc] = np.dot(loc_val, score_dist)
    return max(expected, key=expected.get)
                    
def next_settlement(self):        
    locations = set()
    potential_places = self.get_roads()
    if len(potential_places) > 0:
        for road in potential_places:
            if self.board.if_can_build("settlement", road[0][0], road[0][1], self.player_id):
                locations.add(road[0])
            if self.board.if_can_build("settlement", road[1][0], road[1][1], self.player_id):
                locations.add(road[1])
    else:
        for i in range(self.board.height+1):
            for j in range(self.board.width+1):
                if self.if_can_build("settlement", i, j, self.player_id):
                    locations.add((i, j))
    return best_loc(locations)

def next_city(self):
    for i in range(self.board.height+1):
        for j in range(self.board.width+1):
            if self.if_can_build("city", i, j, self.player_id):
                locations.add((i, j))
    return best_loc(locations)
                    
def next_road(self):
    score_dist = priority_resources[self.points]
    expectation = dict()
    locations = []
    for i in range(self.board.height):
        for j in range(self.board.width):
            if self.board.if_can_build_road((i, j), (i+1, j), self.player_id):
                locations.append(((i, j), (i+1, j)))
            if self.board.if_can_build_road((i, j), (i, j+1), self.player_id):
                locations.append(((i, j), (i, j+1)))
        if self.board.if_can_build_road((i, self.board.width), (i+1, self.board.width), self.player_id):
                locations.append(((i, self.board.width), (i+1, self.board.width)))
    for j in range(self.board.width):
        if self.board.if_can_build_road((self.board.height, j), (self.board.height, j+1), self.player_id):
            locations.append(((self.board.height, j), (self.board.height, j+1)))
    
    for loc in locations:
        vec = np.array([0, 0, 0])
        s = loc[0]
        e = loc[1]
        if(s[0] == 0 and e[0] == 0) or (s[1] == 0 and e[1] == 0):
            vec[self.board.resources[s[0], s[1]]] += probs[self.dice[s[0], s[1]]]
        elif(s[0] == self.board.height and e[0] == self.board.height):
            vec[self.board.resources[self.board.height-1, s[1]]] += probs[self.dice[self.board.height-1, s[1]]]
        elif(s[1] == self.board.width and e[1] == self.board.width):
            vec[self.board.resources[s[0], self.board.width-1]] += probs[s[0], self.dice[self.board.width-1]]
        elif(s[0] == e[0]):
            vec[self.board.resources[s[0], s[1]]] += probs[self.dice[s[0], s[1]]]
            vec[self.board.resources[s[0]-1, s[1]]] += probs[self.dice[s[0]-1, s[1]]]
        else:
            vec[self.board.resources[s[0], s[1]]] += probs[self.dice[s[0], s[1]]]
            vec[self.board.resources[s[0], s[1]-1]] += probs[self.dice[s[0], s[1]-1]]
        expectation[loc] = np.dot(vec, score_dist)
    return max(expected, key=expected.get)
