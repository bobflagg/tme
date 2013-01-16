import MySQLdb as mdb
import psycopg2 #@UnresolvedImport
from util import word_tokenize_doc

class DataManager(object):
    '''
    A simple facade for managing interactions with the Truonex database.
    '''
    def __init__(self):
        '''
        Initializes this data manager instance with the given configuration.
            @param config: Application wide configuration information.
        '''
        host = 'localhost'
        dbname = 'truonex'
        conn_string = "host='%s' dbname='%s'" % (host, dbname)
        self.conn = psycopg2.connect(conn_string)
  
    def get_records(self, query):    
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def get_tags(self, project_id):
        '''
        Returns user assigned tags for the project with the given id.
        '''
        cursor = self.conn.cursor()
        query = '''
            SELECT
                t.tag
            FROM
                public.tags t
            WHERE
                t.tagable_id = %d
            AND
                t.tagable_type = 'Project' 
            AND
                t.sys_tag = 'user' 
        ''' % project_id 
        return self.get_records(query)

    def get_ciid_projects(self):
        '''
        Returns ids and source urls for all ciid projects.
        '''
        cursor = self.conn.cursor()
        query = '''
            SELECT 
                p.id, p.source_url 
            FROM 
                public.projects p 
            WHERE 
                p.source_url LIKE '%ciid.dk%'
        '''
        return self.get_records(query)

    def get_project_source(self):
        '''
        Returns ids and source urls for all projects with non null source urls.
        '''
        cursor = self.conn.cursor()
        query = '''
            SELECT 
                p.id, p.source_url 
            FROM 
                public.projects p 
            WHERE
                P.source_url IS NOT NULL
        '''
        return self.get_records(query)
    
    def get_project_data(self):    
        query = '''
            SELECT
                p.id, p.title, p.description, p.source_url
            FROM
                public.projects p
            WHERE
                p.status = 'published' 
            AND
                p.deleted = 'false'
        '''
        projects = []
        for record in self.get_records(query): 
            project = ProjectInfo(record)
            project.load_sections(self)
            project.load_sections(self)
            project.load_tags(self)
            content = project.extract_text()
            projects.append({
                'id':project.id,
                'title':project.title,
                'url':project.source_url,
                'text':list(word_tokenize_doc(content.lower())),
                'content':content,
                'tags':project.tags
            })
        return projects

        
    def commit(self):
        self.conn.commit()
        
    def rollback(self):
        self.conn.rollback()
        
    def clear_topics(self):
        '''
        Removes previously added topics.
        '''
        try:
            cursor = self.conn.cursor()
            command = "DELETE FROM public.topics;"                
            cursor.execute(command)
            self.conn.commit()
        except psycopg2.DatabaseError, e:    
            print e.message
            if self.conn:
                self.conn.rollback()
                raise Exception("Could not clear topics.")
        
    def add_topic(self, topic_id, topic_name):
        '''
        Adds the given topic tag to the project with the given id.
        '''
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO public.topics (topic_id, topic_name, created_at, updated_at) VALUES (%d, '%s', 'now', 'now')" % (topic_id, topic_name))
        
    def clear_topic_tags(self, sys_tag='system'):
        '''
        Removes previously added project topic tags.
        '''
        try:
            cursor = self.conn.cursor()
            command = "DELETE FROM public.tags WHERE sys_tag = '%s';" % sys_tag
            cursor.execute(command)
            self.conn.commit()
        except psycopg2.DatabaseError, e:    
            print e.message
            if self.conn:
                self.conn.rollback()
                raise Exception("Could not clear topic tags.")
        
    def get_tags(self, project_id):
        '''
        Returns user assigned tags for the project with the given id.
        '''
        cursor = self.conn.cursor()
        query = '''
            SELECT
                t.tag
            FROM
                public.tags t
            WHERE
                t.tagable_id = %d
            AND
                t.tagable_type = 'Project' 
            AND
                t.sys_tag = 'user' 
        ''' % project_id 
        return self.get_records(query)
        
    def add_tag(self, project_id, topic_tag):
        '''
        Adds the given topic tag to the project with the given id.
        '''
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO public.tags (tagable_id, tagable_type, tag, sys_tag, created_at, updated_at) VALUES (%d, '%s', '%s', 'system', 'now', 'now')" % (project_id, 'Project', topic_tag))
        
    def update_similar(self, project_id, yaml_string):
        try:
            #print 'UPDATE public.projects SET "similar"=%s WHERE id=%s', (yaml_string, project_id)
            cursor = self.conn.cursor()
            cursor.execute('UPDATE public.projects SET "similar"=%s WHERE id=%s', (yaml_string, project_id))
            self.conn.commit()
        except psycopg2.DatabaseError, e:    
            if self.conn:
                self.conn.rollback()
                raise Exception("Could not update project record: id = %s; similar = %s" % ( project_id, yaml_string))
        
    def clear_similars_table(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM public.similars;")
            cursor.execute("SELECT setval('similars_id_seq', 1);")           
            self.conn.commit()
        except psycopg2.DatabaseError, e:    
            print e.message
            if self.conn:
                self.conn.rollback()
                raise Exception("Could not clear similars table.")
        
    def record_similar(self, project_id, similar_id, score):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO public.similars (score, project_id, similar_id, created_at, updated_at) VALUES (%d, %d, %d, 'now', 'now')" % (score, project_id, similar_id))
            
class ProjectInfo(object):   
    """
    Encapsulation of information about an Truonex project provided.
    """
    def __init__(self, record):
        """
        Initializes this project info instance.        
            @param record: A tuple with attribute values for a project.
        """       
        self.id = record[0]
        self.title = record[1]
        self.description = record[2]
        self.source_url = record[3]
        self.sections = []
        
    def load_sections(self, dbm):
        query = '''
            SELECT
                s.id, s.title, s.content
            FROM
                public.sections s
            WHERE
                s.project_id = %s
        ''' % self.id
        for record in dbm.get_records(query):
            section = SectionInfo(record)
            section.load_widgets(dbm)
            if len(section.widgets) > 0:
                self.sections.append(section)          
        
    def load_tags(self, dbm):
        query = '''
            SELECT
                t.tag
            FROM
                tags t
            WHERE
                t.tagable_id = %s AND
                t.tagable_type = 'Project' AND
                t.system = 'false'
        ''' % self.id
        #self.tags = [tag[0] for tag in dbm.get_records(query)]     
        self.tags = []     
        
    def __str__(self):
        return '%s: %s\n%s\n--> %s' % (
            self.id,
            self.title,
            self.description,
            "\n--> ".join(str(section) for section in self.sections)
        )
    
    def __unicode__(self):
         return u'%s: %s\n%s\n\t%s' % (
            self.id,
            self.title,
            self.description,
            "\n\t".join([section.title for section in self.sections])
        )
         
    def extract_text(self):
        pieces = [self.title.strip() + ". "]
        if self.description: pieces.append(self.description)
        for section in self.sections:
            section.extract_text(pieces)
        pieces.append(". ".join(self.tags))
        return " ".join(pieces)

class SectionInfo(object):   
    """
    Encapsulation of information about an Truonex project section.
    """
    def __init__(self, record):
        """
        Initializes this section info instance.        
            @param record: A tuple with attribute values for a section.
        """       
        self.id = record[0]
        self.title = record[1]
        self.widgets = []
        
    def load_widgets(self, dbm):
        query = '''
            SELECT
                w.id, w.content, w.type
            FROM
                public.widgets w
            WHERE
                w.section_id = %s AND
                w.type = 'TextWidget' AND
                char_length(w.content) > 0;
        ''' % self.id
        for record in dbm.get_records(query):
            self.widgets.append(WidgetInfo(record))
        
    def __str__(self):
        return '%s: %s\n%s' % (
            self.id,
            self.title,
            "\n--> ".join(str(widget) for widget in self.widgets)
        )
    
    def __unicode__(self):
        return '%s: %s\n%s' % (
            self.id,
            self.title,
            "\n--> ".join(str(widget) for widget in self.widgets)
        )
                 
    def extract_text(self, pieces):
        for widget in self.widgets:
            widget.extract_text(pieces)

class WidgetInfo(object):   
    """
    Encapsulation of information about an Truonex project section.
    """
    def __init__(self, record):
        """
        Initializes this widget info instance.        
            @param record: A tuple with attribute values for a widget.
        """       
        self.id = record[0]
        self.content = record[1]
        self.type = record[2]
        
    def __str__(self):
        return '%s [%s]: %s' % (
            self.id,
            self.type,
            self.content
        )
    
    def __unicode__(self):
        return '%s [%s]: %s' % (
            self.id,
            self.type,
            self.content
        )  
                 
    def extract_text(self, pieces):
        if self.content: pieces.append(self.content)


class MLDataManager(object):
    '''
    A simple facade for managing interactions with the Media Lab database.
    '''
    def __init__(self):
        '''
        Initializes this data manager instance.
        '''
        self.conn = mdb.connect('localhost', 'truonex', 'purnA12', 'medialab', charset='utf8');
  
    def close(self):    
        self.conn.close()      
        
    def get_records(self, query):    
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    
    def get_project_data(self):   
        # first collect all projects 
        query = '''
            SELECT
                g.id, g.name, g.longDescription
            FROM
                groups g
            WHERE
                g.groupTypeID = 30 
        '''
        projects = {}
        for record in self.get_records(query): 
            id = record[0]
            project = {
                'id':id,
                'name':record[1],
                'description':record[2],
                'url':'-'         
            }
            projects[id] = project
        # now get groups   
        query = '''
            SELECT
                g.id, g.name, g.longDescription
            FROM
                groups g
            WHERE
                g.groupTypeID = 40 
        '''
        groups = {}
        for record in self.get_records(query): 
            id = record[0]
            group = {
                'id':id,
                'name':record[1],
                'description':record[2],
                'url':'-'                        
            }
            groups[id] = group
        # get url if available
        query = '''
            SELECT
                gr.groupID, rs.url
            FROM
                groupResources gr, resources rs
            WHERE
                rs.resourceTypeID = 30
            AND
                rs.id = gr.resourceID
        '''
        for record in self.get_records(query): 
            id = record[0]
            if id in projects:
                project = projects[id]
                project['url'] = record[1]
            if id in groups:
                group = groups[id]
                group['url'] = record[1]
        # finally link projects to groups   
        query = '''
            SELECT
                ga.childID, ga.parentID
            FROM
                groupAffiliations ga, groups g
            WHERE
                g.id = ga.parentID and
                g.groupTypeID=40        
        '''
        for record in self.get_records(query): 
            childID = record[0]
            parentID = record[1]
            if childID in projects: projects[childID]['groupID'] = parentID
        return groups, projects
