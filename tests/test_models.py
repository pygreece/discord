from bot.models import Member


async def test_member_get_by_id(test_session):
    """Test getting a member by ID."""
    # Create a test member
    member = Member(id=123)
    test_session.add(member)
    await test_session.commit()

    # Test get_by_id
    result = await Member.get_by_id(123, session=test_session)
    assert result is not None
    assert result.id == 123
    assert result.dm_sent is False
    assert result.reacted is False

    # Test with non-existent ID
    result = await Member.get_by_id(456, session=test_session)
    assert result is None


async def test_member_get_or_create(test_session):
    """Test getting or creating a member."""
    # Test creating a new member
    member, created = await Member.get_or_create(456, session=test_session)
    await test_session.commit()

    assert created is True
    assert member.id == 456
    assert member.dm_sent is False
    assert member.reacted is False

    # Test getting an existing member
    member2, created2 = await Member.get_or_create(456, session=test_session)

    assert created2 is False
    assert member2.id == 456
    assert member2.dm_sent is False
    assert member2.reacted is False
