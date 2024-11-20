import random


def giver_receiver_matching(members: list) -> None:
    """
    Creates matches for group members.

    * Shuffles group's members into a new list; ensuring the two lists' last
    members are not the same.
    * Iterates through the original list picking a group member from the shuffled
    list and removing it from the list. Always ensuring the two members are not
    the same.
    """
    shuffled_members = members.copy()
    random.shuffle(shuffled_members)

    if shuffled_members[-1] == members[-1]:
        shuffled_members = shuffled_members[1:] + [shuffled_members[0]]

    for giver in members:
        for i, receiver in enumerate(shuffled_members):
            if giver == receiver:
                continue
            giver.recipient = receiver
            giver.save()
            shuffled_members.pop(i)
            break
