from datetime import datetime, timedelta

from app import db, celery


@celery.task(name="update_statistics")
def update_statistics(date_str=None):
    """ Update relation_statistics, sender_statistics, receiver_statistics (all depend on coverage_statistics)."""

    if date_str is None:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

    # Update relation statistics
    db.session.execute(f"""
        DELETE FROM relation_statistics
        WHERE date = '{date_str}';

        INSERT INTO relation_statistics AS rs (date, sender_id, receiver_id, is_trustworthy, max_distance, max_normalized_quality, messages_count, coverages_count)
        SELECT
            tmp.date,
            tmp.sender_id,
            tmp.receiver_id,

            is_trustworthy,

            MAX(tmp.max_distance) AS max_distance,
            MAX(tmp.max_normalized_quality) AS max_normalized_quality,
            SUM(tmp.messages_count) AS messages_count,
            COUNT(DISTINCT tmp.location_mgrs_short) AS coverages_count
        FROM coverage_statistics AS tmp
        WHERE tmp.date = '{date_str}'
        GROUP BY date, sender_id, receiver_id, is_trustworthy;
    """)

    # Update sender statistics
    db.session.execute(f"""
        DELETE FROM sender_statistics
        WHERE date = '{date_str}';

        INSERT INTO sender_statistics AS rs (date, sender_id, is_trustworthy, max_distance, max_normalized_quality, messages_count, coverages_count, receivers_count)
        SELECT
            tmp.date,
            tmp.sender_id,

            is_trustworthy,

            MAX(tmp.max_distance) AS max_distance,
            MAX(tmp.max_normalized_quality) AS max_normalized_quality,
            SUM(tmp.messages_count) AS messages_count,
            COUNT(DISTINCT tmp.location_mgrs_short) AS coverages_count,
            COUNT(DISTINCT tmp.receiver_id) AS receivers_count
        FROM coverage_statistics AS tmp
        WHERE tmp.date = '{date_str}'
        GROUP BY date, sender_id, is_trustworthy;
    """)

    # Update receiver statistics
    db.session.execute(f"""
        DELETE FROM receiver_statistics
        WHERE date = '{date_str}';

        INSERT INTO receiver_statistics AS rs (date, receiver_id, is_trustworthy, max_distance, max_normalized_quality, messages_count, coverages_count, senders_count)
        SELECT
            tmp.date,
            tmp.receiver_id,

            is_trustworthy,

            MAX(tmp.max_distance) AS max_distance,
            MAX(tmp.max_normalized_quality) AS max_normalized_quality,
            SUM(tmp.messages_count) AS messages_count,
            COUNT(DISTINCT tmp.location_mgrs_short) AS coverages_count,
            COUNT(DISTINCT tmp.sender_id) AS senders_count
        FROM coverage_statistics AS tmp
        WHERE tmp.date = '{date_str}'
        GROUP BY date, receiver_id, is_trustworthy;
    """)

    # Update receiver rankings
    db.session.execute(f"""
        DELETE FROM receiver_rankings
        WHERE date = '{date_str}';

        INSERT INTO receiver_rankings AS rr (date, receiver_id, country_id, local_distance_pareto, global_distance_pareto, max_distance, max_normalized_quality, messages_count, coverages_count, senders_count)
        SELECT
            rs.date,
            rs.receiver_id,

            r.country_id,
            1.0 * RANK() OVER (PARTITION BY rs.date, r.country_id ORDER BY rs.max_distance) / COUNT(rs.*) OVER (PARTITION BY rs.date, r.country_id) AS local_distance_pareto,
            1.0 * RANK() OVER (PARTITION BY rs.date ORDER BY rs.max_distance) / COUNT(rs.*) OVER (PARTITION BY rs.date) AS global_distance_pareto,

            rs.max_distance,
            rs.max_normalized_quality,
            rs.messages_count,
            rs.coverages_count,
            rs.senders_count
        FROM receiver_statistics AS rs
        LEFT JOIN receivers AS r ON rs.receiver_id = r.id
        WHERE rs.date = '{date_str}' AND rs.is_trustworthy IS TRUE;
    """)

    db.session.commit()


@celery.task(name="update_sender_direction_statistics")
def update_sender_direction_statistics():
    """ Update sender_direction_statistics."""

    db.session.execute("""
        DELETE FROM sender_direction_statistics;

        INSERT INTO sender_direction_statistics(sender_id, receiver_id, directions_count, messages_count, direction_data)
        SELECT
            sq2.sender_id,
            sq2.receiver_id,
            COUNT(sq2.*) AS directions_count,
            SUM(sq2.messages_count) AS messages_count,
            json_agg(json_build_object('direction', direction, 'messages_count', messages_count, 'max_range', max_range)) AS direction_data
        FROM (
            SELECT
                sq.sender_id,
                sq.receiver_id,
                sq.direction,
                COUNT(sq.*) AS messages_count,
                MAX(sq.max_range) AS max_range
            FROM (
                SELECT
                    s.id AS sender_id,
                    r.id AS receiver_id,
                    10000 * 10^(sp.normalized_quality/20.0) AS max_range,
                    CASE
                        WHEN sp.bearing-sp.track < 0
                        THEN CAST((sp.bearing-sp.track+360)/10 AS INTEGER)*10
                        ELSE CAST((sp.bearing-sp.track)/10 AS INTEGER)*10
                    END AS direction
                FROM sender_positions AS sp
                INNER JOIN senders s ON sp.name = s.name
                INNER JOIN receivers r ON sp.receiver_name = r.name
                WHERE
                    sp.track IS NOT NULL AND sp.bearing IS NOT NULL AND sp.normalized_quality IS NOT NULL
                    AND sp.agl >= 200
                    AND turn_rate BETWEEN -10.0 AND 10.0
                    AND climb_rate BETWEEN -3.0 AND 3.0
            ) AS sq
            GROUP BY sq.sender_id, sq.receiver_id, sq.direction
            ORDER BY sq.sender_id, sq.receiver_id, sq.direction
        ) AS sq2
        GROUP BY sq2.sender_id, sq2.receiver_id;
    """)
