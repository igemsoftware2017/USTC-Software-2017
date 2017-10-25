use igem;
DROP PROCEDURE IF EXISTS filter_parts;
delimiter //
CREATE PROCEDURE filter_parts ()
BEGIN
    DROP TABLE IF EXISTS parts_filtered;
    CREATE TABLE `parts_filtered` (
        `part_id` int(11) NOT NULL AUTO_INCREMENT,
        `ok` tinyint(1) DEFAULT '1',
        `part_name` varchar(255) NOT NULL,
        `short_desc` varchar(100) DEFAULT NULL,
        `description` longtext,
        `part_type` varchar(20) DEFAULT NULL,
        `author` varchar(200) DEFAULT NULL,
        `owning_group_id` int(11) DEFAULT NULL,
        `status` varchar(20) DEFAULT NULL,
        `dominant` tinyint(1) DEFAULT '0',
        `informational` tinyint(1) DEFAULT '0',
        `discontinued` int(11) DEFAULT '0',
        `part_status` varchar(40) DEFAULT '',
        `sample_status` varchar(40) DEFAULT '',
        `p_status_cache` varchar(1000) DEFAULT '',
        `s_status_cache` varchar(1000) DEFAULT '',
        `creation_date` date DEFAULT NULL,
        `m_datetime` datetime DEFAULT NULL,
        `m_user_id` int(11) DEFAULT '0',
        `uses` int(11) DEFAULT '-1',
        `doc_size` int(11) DEFAULT '0',
        `works` varchar(10) NOT NULL DEFAULT '',
        `favorite` int(4) DEFAULT '0',
        `specified_u_list` longtext,
        `deep_u_list` longtext,
        `deep_count` int(11) DEFAULT '0',
        `ps_string` longtext,
        `scars` varchar(20) DEFAULT '10',
        `default_scars` varchar(20) NOT NULL DEFAULT '10',
        `owner_id` int(11) DEFAULT NULL,
        `group_u_list` longtext,
        `has_barcode` tinyint(1) DEFAULT '0',
        `notes` longtext,
        `source` text NOT NULL,
        `nickname` varchar(10) DEFAULT '',
        `categories` varchar(500) DEFAULT '',
        `sequence` longtext NOT NULL,
        `sequence_sha1` binary(20) DEFAULT NULL,
        `sequence_update` int(11) NOT NULL DEFAULT '5',
        `seq_edit_cache` longtext,
        `review_result` double(12,0) DEFAULT NULL,
        `review_count` int(4) DEFAULT NULL,
        `review_total` int(4) DEFAULT NULL,
        `flag` int(4) DEFAULT NULL,
        `sequence_length` int(11) DEFAULT '0',
        `temp_1` int(11) DEFAULT NULL,
        `temp_2` int(11) DEFAULT NULL,
        `temp_3` int(11) DEFAULT NULL,
        `temp4` int(11) DEFAULT NULL,
        `rating` int(11) DEFAULT '0',
        `status_w` double DEFAULT NULL,
        `sample_status_w` double DEFAULT NULL,
        `works_w` double DEFAULT NULL,
        `doc_size_w` double DEFAULT NULL,
        `uses_w` double DEFAULT NULL,
        `review_total_w` double DEFAULT NULL,
        `review_count_w` double DEFAULT NULL,
        `deep_count_w` double DEFAULT NULL,
        `has_subpart` tinyint(1),
        `ac` longtext,
        `ruler` longtext,
        PRIMARY KEY (`part_name`),
        KEY `parts_id_ix` (`part_id`),
        KEY `parts_name_ix` (`part_name`),
        KEY `deep_count_ix` (`deep_count`),
        KEY `status.ix` (`status`),
        KEY `parts_deep_u_ix` (`deep_u_list`(20)),
        KEY `sequence_sha1_ix` (`sequence_sha1`),
        KEY `category_ix` (`categories`(10))
    ) ENGINE MyISAM;
    INSERT INTO parts_filtered
        SELECT p.*,
            CASE
                WHEN p.status = 'Available' or p.status = 'Informational' THEN 1.0
                WHEN p.status = 'Planning' THEN 0.5
                WHEN p.status = 'Deleted' or p.status = 'Unavailable' THEN 0
            END AS status_w,
            CASE
                WHEN p.sample_status = 'Discontinued' or p.sample_status = 'No part sequence' THEN 0
                WHEN p.sample_status = 'It\'s complicated' or p.sample_status = 'For reference only' THEN 0.4
                WHEN p.sample_status = '' THEN 0.5
                WHEN p.sample_status = 'Not in stock' THEN 0.7
                WHEN p.sample_status = 'In stock' THEN 1.0
            END as sample_status_w,
            CASE
                WHEN p.works = 'Fails' or p.works = 'None' THEN 0.1
                WHEN p.works = 'Issues' THEN 0.5
                WHEN p.works = 'Works' THEN 1.0
                ELSE NULL
            END as works_w,
            LOG(t.ds_gap, doc_size - t.ds_inf + 1) as doc_size_w,
            LOG(t.uses_gap, uses - t.uses_inf + 1) as uses_w,
            COALESCE(
                LOG(t.rt_gap, review_total - t.rt_inf + 1),
                0
            ) as review_total_w,
            COALESCE(
                LOG(t.rc_gap, review_count - t.rc_inf + 1),
                0
            ) as review_count_w,
            (deep_count - dc_inf) / dc_gap as deep_count_w,
            0 as has_subpart,
            '' as ac,
            '' as ruler
        FROM
            parts AS p,
            (SELECT
                MIN(doc_size) as ds_inf,
                MAX(doc_size) - MIN(doc_size) + 1 as ds_gap,
                MIN(uses) as uses_inf,
                MAX(uses) - MIN(uses) + 1 as uses_gap,
                MIN(review_count) as rc_inf,
                MAX(review_count) - MIN(review_count) + 1 as rc_gap,
                MIN(review_total) as rt_inf,
                MAX(review_total) - MIN(review_total) + 1 as rt_gap,
                MIN(deep_count) as dc_inf,
                MAX(deep_count) - MIN(deep_count) as dc_gap
            FROM parts) AS t
        WHERE sequence_length > 10
        AND part_name NOT IN (
            SELECT part_name FROM parts
            GROUP BY part_name HAVING COUNT(part_name) > 1
        );
END//
delimiter ;
