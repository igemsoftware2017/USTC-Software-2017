DROP VIEW IF EXISTS parts;
CREATE VIEW parts AS SELECT * from igem.parts_filtered;
DROP VIEW IF EXISTS biobricks;
CREATE VIEW biobricks AS
    SELECT
        w.weight as weight,
        m.group_name as group_name,
        m.experience_status as experience_status,
        m.twin_num as twin_num,
        m.parameters as parameters,
        m.rates as rates,
        m.rate_score as rate_score,
        m.stars as stars,
        m.document_id as document_id,
        m.watches as watches,
        m.last_fetched as last_fetched,
        p.part_id as part_id,
        p.ok as ok,
        p.part_name as part_name,
        p.short_desc as short_desc,
        p.description as description,
        p.part_type as part_type,
        p.author as author,
        p.status as status,
        p.dominant as dominant,
        p.part_status as part_status,
        p.sample_status as sample_status,
        p.creation_date as creation_date,
        p.uses as uses,
        p.works as works,
        p.favorite as favorite,
        p.has_barcode as has_barcode,
        p.nickname as nickname,
        p.categories as categories,
        p.sequence as sequence,
        p.sequence_length as sequence_length,
        p.review_count as review_count,
        p.review_total as review_total,
        p.ac as ac,
        p.ruler as ruler
    FROM
        igem.parts_filtered as p
        LEFT JOIN biobrick_biobrickmeta as m ON m.part_name = p.part_name
        LEFT JOIN biobrick_biobrickweight as w ON w.part_name = p.part_name;
