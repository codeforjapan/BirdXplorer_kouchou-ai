import { BaseCard } from "@/components/BaseCard";
import type { Cluster } from "@/type";
import { Box, Flex, Text } from "@chakra-ui/react";
import { MessageSquareIcon } from "lucide-react";

type Props = {
  cluster: Cluster;
};

export function ClusterOverview({ cluster }: Props) {
  const title = (
    <Flex alignItems="center" gap={2} color="white">
      <MessageSquareIcon size={18} color="#38bdf8" />
      <Text as="span" color="#38bdf8" fontWeight="bold">
        {cluster.value.toLocaleString()}件
      </Text>
      <Text as="span" ml={2}>
        {cluster.label}
      </Text>
    </Flex>
  );

  const body = (
    <Text color="gray.300" fontSize="sm" lineHeight="tall">
      {cluster.takeaway}
    </Text>
  );

  return (
    <Box id={cluster.label} w="100%">
      <BaseCard title={title} body={body} titleBgColor="#000000" />
    </Box>
  );
}
