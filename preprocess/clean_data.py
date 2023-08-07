# FeatCode Preprocessing
# author: Scott Skibin

premium_probs = ["missing ranges",
                 "flatten 2d vector",
                 "meeting rooms ii",
                 "alien dictionary",
                 "find the celebrity",
                 "inorder successor in bst",
                 "range sum query 2d mutable",
                 "longest substring with at most k distinct characters",
                 "design tic tac toe"]

new_txt_file = open("data/default_urls.txt","w")
lines_seen = set()
with open("data/leet_urls.txt", "r") as txt_file:
    lines = txt_file.readlines()
    for line in lines:
        stripped_line = line.strip('\n')
        items = line.split(',')
        if stripped_line not in lines_seen and items[0] not in premium_probs:
            lines_seen.add(stripped_line)
            new_txt_file.write(line)
           
txt_file.close()
new_txt_file.close()