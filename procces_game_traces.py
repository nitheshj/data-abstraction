

if __name__ == "__main__":
    few = ['few_dots_plaque','few_dots']
    many = ['pick_up_plaque','download_stars','many_dots_painting','many_dots_painting_plaque']
    glyph_cypher = ['abstract_symbols','abstract_symbols_plaque']
    cypher_wheel =  ['download_cypher_wheel','download_cypher_directions']
    safari = ['safari','safari_plaque','all_safari_pics']
    safe = ['safe','code safe']
    cues = few+many+glyph_cypher+cypher_wheel+safari+safe
    filename = 'gameTraces/stage_1.csv'
    with open(filename) as f:
        data = f.readlines()
    data = data[1:]
    current_puzzle = 'few' 
    teams = []
    players = []
    seqs = []
    threshold = 8
    max_v = 0
    for entry in data:
        safari_done = False
        puzzle_done = {'few':False,'many':False,'glyph':False,'cypher':False,'safe':False,'safari':False}
        revised_cues = []
        entry = entry.replace('\n','')
        comps = entry.split(',')
        team = comps[0]
        stage = comps[1]
        player = comps[2]
        seq = comps[3:]
        players.append(player)
        teams.append(team)
        for el in seq:
            isRelevant = False
            isSolution = False
            entry = ''
            captin = ''


            if 'True' in el:
                if 'random' in el:
                    current_puzzle = 'many'
                    captin = 'solved_few_dots'
                    puzzle_done['few'] = True
                    num_correct = 0
                elif 'hole' in el:
                    current_puzzle = 'glyph'
                    puzzle_done['many'] = True
                    captin = 'solved_many_dots'
                elif 'glyph' in el:
                    current_puzzle = 'cypher'
                    puzzle_done['glyph'] = True
                    captin = 'solved_glyph'
                elif 'orb' in el:
                    current_puzzle = 'safe'
                    puzzle_done['cypher'] = True
                    captin = 'solved_cypher'
                elif 'safari' in el:
                    safari_done = True
                    puzzle_done['safari'] = True
                    captin = 'solved_safari'
                elif 'safe' in el:
                    puzzle_done['safe'] = True
                    safe_done = True
                    captin = 'solved_safe'
                isSolution = True
                relevantInSeq = False
                for i,prev_el in enumerate(revised_cues[-threshold:]):
                    if 'relevant' in prev_el:
                        relevantInSeq = True
                if not relevantInSeq:
                    revised_cues.append('no_relevant')
                    # print(revised_cues[-threshold:]) 


            elif 'False' in el:
                isSolution = True
                captin = 'failed_once'
            elif 'failed' in el:
                isSolution = True
                captin = el

            elif el not in cues:
                if 'gave_up_without_trying' in el:
                    revised_cues.append(el)
                else:
                    revised_cues.append('navigation')
                continue

            if isSolution:
                entry = captin
            else:
                if current_puzzle == 'few':
                    if safari_done:
                        if (el in few) or (el in safari):
                            isRelevant = True
                    else:
                        if (el in few): 
                            isRelevant = True

                elif current_puzzle == 'many':
                    if safari_done:
                        if (el in many) or (el in safari):
                            isRelevant = True
                    else:
                        if (el in many): 
                            isRelevant = True

                elif current_puzzle == 'glyph':
                    if safari_done:
                        if (el in glyph_cypher) or (el in safari):
                            isRelevant = True
                    else:
                        if (el in glyph_cypher): 
                            isRelevant = True

                elif current_puzzle == 'cypher':
                    if safari_done:
                        if (el in cypher_wheel) or (el in safari):
                            isRelevant = True
                    else:
                        if (el in cypher_wheel): 
                            isRelevant = True

                elif current_puzzle == 'safe':
                    if safari_done:
                        if (el in safe) or (el in safari):
                            isRelevant = True
                    else:
                        if (el in safe): 
                            isRelevant = True
            if isSolution:
                revised_cues.append(entry)
            else:
                if isRelevant:
                    revised_cues.append('relevant_cue')
                else:
                    revised_cues.append('irrelevant_cue')

        if not puzzle_done['safe']:
            num_correct = 0
            for puz in puzzle_done:
                if puzzle_done[puz]:
                    num_correct+= 1
            revised_cues.append('gave_up_'+str(num_correct))
        seqs.append(revised_cues)

    # for seq in seqs:
    #     if len(seq) > max_v:
    #         max_v = len(seq)
    # for seq in seqs:
    #     if len(seq)<max_v:
    #         for i in range(max_v - len(seq)):
    #             seq.append('NULL')
    f = open('gameTraces/stage_1_processed.csv','w')
    f.write("player,team,sequence\n")
    for i,seq in enumerate(seqs):
        line = players[i] + ',' + teams[i]+','
        for el in seq:
            line+=el+','
        line = line[:-1]
        line += '\n'
        f.write(line)

