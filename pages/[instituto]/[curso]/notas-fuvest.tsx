import Typography from "@material-ui/core/Typography";
import Box from "@material-ui/core/Box";
import NotaTable from "../../../src/components/NotaFuvestTable";

import { getData } from "dataprovider/lib";
import { GetStaticProps, GetStaticPaths } from "next";
import {
  CursoEntity,
  InstitutoEntity,
  ManualDoVestibulandoEntity,
  NotaFuvestEntity,
} from "core/src/Entity";
import Layout from "../../../src/components/Layout";

type FuvestPageType = {
  notas: NotaFuvestEntity[];
  curso: CursoEntity;
  instituto: InstitutoEntity;
};

const FuvestPage = ({ notas, curso, instituto }: FuvestPageType) => (
  <Layout>
    <Box my={4}>
      <Typography variant="h4" component="h1" gutterBottom>
        {curso.nome} ({instituto.sigla}) - Fuvest
      </Typography>
    </Box>
    <NotaTable notas={notas} />
  </Layout>
);
export default FuvestPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  const data: ManualDoVestibulandoEntity = await getData();
  const campusInstitutos = data.campus.flatMap((campus) => campus.institutos);
  const instituto = campusInstitutos.find(
    (instituto) => instituto.sigla == params.instituto
  );
  const curso = instituto.cursos.find((curso) => curso.nome == params.curso);
  const notas = curso.notas.fuvest;

  return {
    props: {
      instituto,
      curso,
      notas,
    },
  };
};

export const getStaticPaths: GetStaticPaths = async () => {
  const data: ManualDoVestibulandoEntity = await getData();
  const campusInstitutos = data.campus.flatMap((campus) => campus.institutos);
  const unidadesCursosList = campusInstitutos.flatMap((instituto) =>
    instituto.cursos.flatMap((curso) => ({
      instituto: instituto.sigla,
      curso: curso.nome,
    }))
  );

  return {
    paths: unidadesCursosList.map((e) => ({ params: e })),
    fallback: false,
  };
};
