CREATE OR REPLACE FUNCTION populate_profiles()
RETURNS void 
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO public.profiles (id, display_name, created_at, incident_count)
    SELECT 
        u.id,
        u.raw_user_meta_data ->> 'display_name' AS display_name,
        u.created_at,
        COALESCE(COUNT(i.id), 0) AS incident_count
    FROM 
        auth.users u
    LEFT JOIN 
        incident i ON u.id = i.user_id
    GROUP BY 
        u.id, u.raw_user_meta_data, u.created_at;
END;
$$;

SELECT populate_profiles();

CREATE OR REPLACE FUNCTION create_profile_on_user_insert()
RETURNS TRIGGER 
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO public.profiles (id, display_name, created_at)
    VALUES (NEW.id, NEW.raw_user_meta_data ->> 'display_name', NEW.created_at);
    RETURN NEW;
END;
$$;