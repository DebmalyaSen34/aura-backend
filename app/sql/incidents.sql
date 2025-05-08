CREATE OR REPLACE FUNCTION get_incidents_with_stats(p_user_id uuid)
RETURNS TABLE (
    incident_id bigint,
    content text,
    user_id uuid,
    display_name text,
    created_at timestamptz,
    total_upvotes bigint,
    total_downvotes bigint,
    total_comments bigint,
    is_upvoted boolean,
    is_downvoted boolean
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        i.id AS incident_id,
        i.content,
        i.user_id,
        u.raw_user_meta_data ->> 'display_name'::text as display_name,
        i.created_at,
        COALESCE(SUM(CASE WHEN v.upvote = 1 THEN 1 ELSE 0 END), 0) AS total_upvotes,
        COALESCE(SUM(CASE WHEN v.downvote = 1 THEN 1 ELSE 0 END), 0) AS total_downvotes,
        COALESCE(COUNT(c.id), 0) AS total_comments,
        COALESCE(BOOL_OR(v.voter_id = p_user_id AND v.upvote = 1), FALSE) AS is_upvoted,
        COALESCE(BOOL_OR(v.voter_id = p_user_id AND v.downvote = 1), FALSE) AS is_downvoted
    FROM 
        incident i
    LEFT JOIN 
        votes v ON i.id = v.incident_id
    LEFT JOIN 
        comments c ON i.id = c.incident_id
    LEFT JOIN 
        auth.users u ON i.user_id = u.id
    WHERE 
        i.user_id != p_user_id  -- Exclude posts created by the user
    GROUP BY 
        i.id, u.raw_user_meta_data, i.content, i.user_id, i.created_at;
END;
$$;