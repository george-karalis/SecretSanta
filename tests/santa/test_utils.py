from unittest import mock

import pytest
from django.contrib.auth.models import User

from secretsanta.santa.models import GroupMember
from secretsanta.santa.utils import giver_receiver_matching


class TestGiverReceiverMatching:
    def create_mock_member(username):
        user = mock.Mock(spec=User, username=username)
        member = mock.Mock(spec=GroupMember)
        member.user = user
        member.recipient = None
        member.save = mock.Mock()  # Mock the save method
        member.__str__ = lambda self: f"Member: {user.username}"
        return member

    member_a = create_mock_member("A")
    member_b = create_mock_member("B")
    member_c = create_mock_member("C")
    member_d = create_mock_member("D")

    @pytest.mark.parametrize(
        "members, shuffled, matches",
        [
            pytest.param(
                [member_a, member_b],
                [member_a, member_b],
                {member_a: member_b, member_b: member_a},
                id="2 Members: Same order",
            ),
            pytest.param(
                [member_a, member_b, member_c],
                [member_a, member_c, member_b],
                {member_a: member_c, member_b: member_a, member_c: member_b},
                id="3 Members: First member is the same",
            ),
            pytest.param(
                [member_a, member_b, member_c, member_d],
                [member_a, member_d, member_c, member_b],
                {
                    member_a: member_d,
                    member_b: member_a,
                    member_c: member_b,
                    member_d: member_c,
                },
                id="4 Members: First member is the same",
            ),
            pytest.param(
                [member_a, member_b, member_c],
                [member_b, member_a, member_c],
                {member_a: member_c, member_b: member_a, member_c: member_b},
                id="3 Members: Last member is the same",
            ),
        ],
    )
    @mock.patch("secretsanta.santa.utils.random")
    def test_perform_matching(self, mock_random, members, shuffled, matches):
        def mock_shuffle(lst):
            lst[:] = shuffled

        mock_random.shuffle.side_effect = mock_shuffle

        giver_receiver_matching(members)

        for giver, receiver in matches.items():
            assert giver.recipient == receiver
