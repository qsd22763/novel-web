UPDATE novel n
INNER JOIN (
    SELECT novel_id, SUM(word_count) as total_wc
    FROM chapter
    GROUP BY novel_id
) c ON c.novel_id = n.id
SET n.word_count = c.total_wc
WHERE n.word_count = 0 AND n.status != 2 AND c.total_wc > 0;
