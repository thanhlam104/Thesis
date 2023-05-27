from neo4j import GraphDatabase
import torch
import pandas as pd
class Recommender():
    def __init__(self, uri, auth = None) -> None:
        self.uri = uri
        if auth == None:
            self.driver = GraphDatabase.driver(uri)
        else:
            self.driver = GraphDatabase.driver(uri,auth)
        self.session = self.driver.session()
    def listToString(self,list):
        n = len(list)
        res = '['
        for i in range(n):
            res +='\''+list[i]+'\''
            if i <n-1:
                res += ','
        res += ']'
        return res
    def readArray(string):
        list = string[1:-1].split(',')
        res = [float(i) for i in list]
        return res
    
    def byGenres(self,genres,mode = 'count', numRec = 5):
        '''
        Create recommendation from a given set of genres
        Parameter:
            - genres: a list of string
            - mode: 2 mode available: 'intersect' and 'jaccard'
            - numRec: integer, number of recommendation in the result
        Output: a dataframe or None
        '''
        if mode == 'jaccard':
            script = '''
            use metacritic2
            with %s as genres
            match p=(g:Genre)--(m:Movie)
            where g.genre in genres
            with m, count(g) as commonGenres, size(genres) as n
            match (m)-[:IN_GENRE]-(g1:Genre)
            with m, commonGenres,count(g1) as total,n
            with m, 1.0*commonGenres/(total+n-commonGenres) as jaccard
            match (u:User)-[:RATED]-(m)
            with m, jaccard, count(u) as popularity
            return m.title as RecommendedMovies,jaccard, popularity
            order by jaccard DESC, popularity DESC
            limit %d
            '''%(self.listToString(genres),numRec)
        elif mode=='intersect':
            script = '''
            use metacritic2
            with %s as genres
            match p=(g:Genre)--(m:Movie)
            where g.genre in genres
            with m, count(g) as commonGenres
            match (u:User)-[:RATED]-(m)
            with m, commonGenres, count(u) as popularity
            return m.title as RecommendedMovies,commonGenres, popularity
            order by commonGenres DESC, popularity DESC
            limit %d
            '''%(self.listToString(genres),numRec)
        else:
            print('Invalid mode')
            return None
        result = self.session.run(script).to_df()

        return result


    def byHistory(self, username, numRec=5):
        '''
        Create recommendation from genres that a user has watched
        Parameter:
            - username: string, username of a specific user
            - numRec: integer, number of recommendation in the result
        Output: a dataframe or None
        '''
        script = '''
        use metacritic2
        match (u:User{uid: '%s'})-[:RATED]-(m:Movie)-[:IN_GENRE]-(g:Genre)-[:IN_GENRE]-(m2:Movie)
        where not exists {(u)-[:RATED]-(m2)}
        with m2, g,count(m) as count
        with m2, collect([g.genre,count]) as genreScore, collect(g.genre) as genres
        with m2,genres, genreScore, reduce(s=0, x in genreScore|s+x[1]) as matchScore
        return m2.title as RecommendedMovies, genres
        order by matchScore desc 
        limit %d
        '''%(username, numRec)
        result = self.session.run(script).to_df()
        return result

    def byUserAlsoWatch(self, movieTitle, numRec=5):
        '''
        Create recommendation from movies that other users who watched this movie also watched
        Parameter:
            - movieTitle: string, title of the current movie
            - numRec: integer, number of recommendation in the result
        Output: a dataframe or None
        '''
        script = '''
        use metacritic2
        match (m:Movie{title:'%s'})-[:RATED]-(u:User)-[:RATED]-(m2:Movie)
        with m2, count(u) as users
        return m2.title as RecommendedMovies, users
        order by users desc 
        limit %d
        '''%(movieTitle,numRec)
        result = self.session.run(script).to_df()
        return result

    def bySimilarity(self, movieTitle, mode='count', numRec=5,properties=None):
        '''
        Recommend movies that are similar to a specific movie
        Parameter:
            - movieTitle
            - mode: 2 mode available: 'count' and 'jaccard'
            - numRec: integer, number of recommendation in the result
        Output: a dataframe or None
        '''
        rel = ''
        if properties != None:
            rel = ':'
            for p in properties:
                rel += p+'|'
            rel = rel[:-1]

        if mode == 'count':
            script = '''
            use metacritic2
            match (m1:Movie{title:'%s'})-[r1%s]-(n)-[r2%s]-(m2:Movie)
            where type(r1) = type(r2)
            and type(r1) <> 'RATED'
            with m2, count(n) as common
            match (m2)-[:RATED]-(u:User)
            with m2, common, count(u) as popularity
            return m2.title as RecommendedMovies, common, popularity
            order by common desc limit %d
            '''%(movieTitle,rel,rel,numRec)

        elif mode == 'jaccard':
            script = '''
            use metacritic2
            match (m1:Movie{title:'%s'})-[r1%s]-(n)-[r2%s]-(m2:Movie)
            where type(r1) = type(r2)
            and type(r1) <> 'RATED'
            with m1,m2, count(n) as intersect
            match (m1)-[r11%s]-(n1) where type(r11) <>'RATED'
            with m1, m2, intersect, count(n1) as m1p
            match (m2)-[r22%s]-(n2) where type(r22) <>'RATED'
            with m1, m2, intersect, m1p, count(n2) as m2p
            return m2.title as RecommendedMovies, 1.0*intersect/(m1p+m2p-intersect) as jaccard
            order by jaccard desc limit %d
            '''%(movieTitle,rel,rel,rel,rel,numRec)

        else:
            print('Invalid mode')
            return None
        
        result = self.session.run(script).to_df()
        return result
    
    def byKNN(self, userid,numRec=5,k=5, mode='cosine'):
        '''
        Create recommendation from movies that similar users watch
        Parameter:
            - movieTitle
            - mode: 2 mode available: 'cosine' and 'pearson'
            - k: number k in knn
            - numRec: integer, number of recommendation in the result
        Output: a dataframe or None
        '''
        if mode == 'cosine':
            script = '''
            use metacritic2
            match (u1:User{uid:'%d'})-[r1:RATED]-(m:Movie)-[r2:RATED]-(u2:User)
            with u1, u2, count(m) as numMovies, sum(toFloat(r1.rating)*toFLoat(r2.rating)) as dotproduct
            where numMovies > 5
            match (u1)-[r3:RATED]-(m:Movie)
            with u1, u2, dotproduct,
            collect(r3.rating) as u1ratings
            match (u2)-[r4:RATED]-(m:Movie)
            with u1, u2,dotproduct, u1ratings, collect(r4.rating) as u2ratings
            with u1, u2,dotproduct,
            sqrt(reduce(s=0.0,x in u1ratings|s + toFloat(x)^2)) as r1length, 
            sqrt(reduce(s=0.0,x in u2ratings|s + toFloat(x)^2)) as r2length
            with u1,u2, dotproduct/(r1length*r2length) as cosineSim
            order by cosineSim desc limit %d
            match (u2)-[r2:RATED]-(rec:Movie)
            where not exists{(u1)-[:RATED]-(rec)}
            with rec, sum(cosineSim*toFloat(r2.rating)) as score
            return rec.title as RecommendedMovies, score
            order by score desc limit %d
            '''%(userid, k, numRec)
        elif mode == 'pearson':
            script = '''
            use metacritic2
            match (u1:User{uid:'%d'})-[r:RATED]-(m:Movie)
            with u1, avg(toFloat(r.rating)) as u1_mean
            match (u1)-[r1:RATED]-()-[r2:RATED]-(u2:User)
            with u1, u1_mean, u2, collect([toFloat(r1.rating),toFloat(r2.rating)]) as ratings where size(ratings)>5
            match (u2)-[r:RATED]-(m:Movie)
            with u1, u1_mean, u2, avg(toFloat(r.rating)) as u2_mean, ratings
            with u1,u2,reduce(s=0.0,x in ratings|s+(x[0]-u1_mean)*(x[1]-u2_mean)) as cov, 
            sqrt(reduce(s=0.0, x in ratings|s+(x[0]-u1_mean)^2)*reduce(s=0.0, x in ratings|s+(x[1]-u2_mean)^2)) as std
            with u1, u2, 1.0*cov/std as pearson
            order by pearson desc limit %d
            match (u2)-[r2:RATED]-(rec:Movie)
            where not exists{(u1)-[:RATED]-(rec)}
            with rec, sum(pearson*toFloat(r2.rating)) as score
            return rec.title as RecommendedMovies, score
            order by score desc limit %d
            '''%(userid, k, numRec)
        else:
            print('Invalid mode')
            return None
        
        result = self.session.run(script).to_df()
        return result
    def byModel(self, userid, numRec = 5, mode='fastRP'):
        '''
        Create recommendation with neural network model
        Parameter:
            - movieTitle
            - mode: 2 mode available: 'fastRP' and 'node2vec'
            - numRec: integer, number of recommendation in the result
        Output: a dataframe or None
        '''
        if mode == 'fastRP':
            script = '''
            use metacritic2
            match (u:User{uid:'%d'})
            with u
            match (m:Movie)
            where not exists {(u)-[:RATED]-(m)}
            return u.fastRPembedding as user, m.fastRPembedding as movie, m.title as movieTitle
            '''%(userid)
            input = self.session.run(script).to_df()
            net = torch.jit.load('model/fastRP_scripted.pt')
            result = []
            with torch.no_grad():
                for index, row in input.iterrows():
                    rating = net(torch.tensor(row.user+row.movie))
                    result.append((row.movieTitle, float(rating)))
                result.sort(key=lambda x:x[1],reverse=True )
                top_result = pd.DataFrame([x[0] for x in result[:numRec]], columns=['RecommendedMovie'])
            return top_result

        elif mode == 'node2vec':
            script = '''
            use metacritic2
            match (u:User{uid:'%d'})
            with u
            match (m:Movie)
            where not exists {(u)-[:RATED]-(m)}
            return u.node2vec as user, m.node2vec as movie, m.title as movieTitle
            '''%(userid)

            input = self.session.run(script).to_df()
            net = torch.jit.load('model/node2vec_scripted.pt')
            result = []
            with torch.no_grad():
                for index, row in input.iterrows():
                    rating = net(torch.tensor(row.user+row.movie))
                    result.append((row.movieTitle, float(rating)))
                result.sort(key=lambda x:x[1],reverse=True )
                top_result = pd.DataFrame([x[0] for x in result[:numRec]], columns=['RecommendedMovie'])
            return top_result
        else:
            print('Invalid mode')
            return None
        

        


            



