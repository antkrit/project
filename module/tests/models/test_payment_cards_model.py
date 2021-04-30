import uuid
from module.tests import setup_database
from module.server.models.payment_cards import Card, UsedCard


def test_create_and_add_cards(setup_database):
    """Creates objects and adds them to the database"""
    db = setup_database

    # Unused card objects
    rand_uuid = str(uuid.uuid4())
    crd = Card(
        uuid=rand_uuid,
        amount=200,
        code='1'.rjust(6, '0')
    )
    crd1 = Card()

    assert crd is not None and crd1 is not None

    # Add to the database
    assert len(db.session.query(Card).all()) == 0
    db.session.add(crd)
    db.session.add(crd1)
    assert len(db.session.query(Card).all()) == 2

    # Fields
    assert db.session.query(Card).get(2).uuid is not None
    assert db.session.query(Card).get(2).amount == 0
    assert db.session.query(Card).get(2).code == '000000'

    # Used card objects
    rand_uuid = str(uuid.uuid4())
    crd = UsedCard(
        uuid=rand_uuid,
        amount=200,
        code='1'.rjust(6, '0'),
        balance_after_use=200,
        user_id=1
    )
    crd1 = UsedCard()

    assert crd is not None and crd1 is not None

    # Add to the database
    assert len(db.session.query(UsedCard).all()) == 0
    db.session.add(crd)
    db.session.add(crd1)
    assert len(db.session.query(UsedCard).all()) == 2

    # Default fields
    assert db.session.query(UsedCard).get(2).uuid is not None
    assert db.session.query(UsedCard).get(2).amount == 0
    assert db.session.query(UsedCard).get(2).code == '000000'
    assert db.session.query(UsedCard).get(2).balance_after_use == 0
    assert db.session.query(UsedCard).get(2).used_at is not None
    assert db.session.query(UsedCard).get(2).user_id is None


def test_methods(setup_database):
    """Tests models methods"""
    db = setup_database

    # Add to the database
    rand_uuid = str(uuid.uuid4())
    rand_uuid1 = str(uuid.uuid4())

    crd = Card(
        uuid=rand_uuid,
        amount=200,
        code='1'.rjust(6, '0')
    )
    used_crd = UsedCard(
        uuid=rand_uuid1,
        amount=200,
        code='2'.rjust(6, '0'),
        balance_after_use=200,
        user_id=1
    )
    db.session.add(crd)
    db.session.add(used_crd)
    db.session.commit()

    # Get card by uuid
    card = Card.get_card_by_uuid(rand_uuid)
    used_card = UsedCard.get_card_by_uuid(rand_uuid1)
    assert card.code == '1'.rjust(6, '0')
    assert used_card.code == '2'.rjust(6, '0')

    # Get card by code
    card = Card.get_card_by_code('1'.rjust(6, '0'))
    assert card.uuid == rand_uuid

    # Representations
    assert card.__repr__() == 'Card #{0}: {1}. Code: {2}'.format(rand_uuid, 200, '1'.rjust(6, '0'))
    assert used_card.__repr__() == 'Card #{0}: used by {1} at {2}. Code: {3}'.format(
        rand_uuid1, 1, used_card.used_at, '2'.rjust(6, '0')
    )
