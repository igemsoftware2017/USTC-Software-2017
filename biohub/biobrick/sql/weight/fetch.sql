SELECT
    p.part_name as part_name,
    p.favorite as favorite,
    p.has_barcode as has_barcode,
    p.status_w as status_w,
    p.sample_status_w as sample_status_w,
    p.works_w as works_w,
    p.uses_w as uses_w,
    p.review_total_w as review_total_w,
    p.review_count_w as review_count_w,
    p.deep_count_w as deep_count_w,
    m.rates as rates,
    m.rate_score as rate_score,
    m.stars as stars,
    m.watches as watches
FROM
    igem.parts_filtered as p
    LEFT JOIN biobrick_biobrickmeta as m ON p.part_name = m.part_name;
